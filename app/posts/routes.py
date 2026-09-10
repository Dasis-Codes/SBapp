from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from app import db
from app.models import Post
from app.posts.forms import PostForm
import bleach
from bleach.css_sanitizer import CSSSanitizer
from app.user.utils import save_picture, process_embedded_images

posts = Blueprint('posts', __name__)

# Allowed CSS styles for highlights, colors, fonts, and image sizing
css_sanitizer = CSSSanitizer(allowed_css_properties=[
    'color', 
    'background-color', 
    'font-size', 
    'font-family', 
    'text-align', 
    'float', 
    'width', 
    'height', 
    'margin', 
    'margin-left', 
    'margin-right'
])

# Allowed HTML Tags
ALLOWED_TAGS = [
    'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'font',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'br', 'span', 'div', 'img', 'mark', 'sub', 'sup'
]

# Allowed Attributes per Tag
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'width', 'height', 'style', 'class'],
    '*': ['style', 'class']
}

# Allowed Protocols for URLs and Images (includes 'data' for base64 images)
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'data']

@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # 1. Sanitize HTML
        clean_content = bleach.clean(
            form.content.data, 
            tags=ALLOWED_TAGS, 
            attributes=ALLOWED_ATTRS,
            protocols=ALLOWED_PROTOCOLS,
            css_sanitizer=css_sanitizer
        )

        # 2. Extract Base64 images, compress them, and replace with static file paths
        final_content = process_embedded_images(clean_content)

        # 3. Save post to database
        post = Post(title=form.title.data, content=final_content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been added!", "success")
        return redirect(url_for("main.home"))
        
    return render_template("create_post.html", title="New Post", form=form, legend="New Post")


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    if post_obj.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        clean_content = bleach.clean(
            form.content.data, 
            tags=ALLOWED_TAGS, 
            attributes=ALLOWED_ATTRS,
            protocols=ALLOWED_PROTOCOLS,
            css_sanitizer=css_sanitizer
        )
        # ADD THIS LINE TO UPDATE ROUTE AS WELL:
        final_content = process_embedded_images(clean_content)

        post_obj.title = form.title.data
        post_obj.content = final_content
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect(url_for("posts.post", post_id=post_obj.id))
        
    elif request.method == "GET":
        form.title.data = post_obj.title
        form.content.data = post_obj.content

    return render_template("create_post.html", title="Update Post", form=form, legend="Update Post")

@posts.route("/post/<int:post_id>")
def post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post_obj.title, post=post_obj)

@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    
    # Allow deletion if current user is the author OR is an admin
    if post_obj.author != current_user and not getattr(current_user, 'is_admin', False):
        abort(403)
        
    db.session.delete(post_obj)
    db.session.commit()
    flash("The post has been deleted!", "success")
    return redirect(url_for("main.home"))