from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from app import db
from app.models import Post
from app.posts.forms import PostForm

posts= Blueprint('posts',__name__)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been added!", "success")
        return redirect(url_for("main.home"))
    return render_template("create_post.html", title="New Post", form=form, legend="New Post")


@posts.route("/post/<int:post_id>")
def post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post_obj.title, post=post_obj)


@posts.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    if post_obj.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post_obj.title = form.title.data
        post_obj.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!", "success")
        return redirect(url_for("posts.post", post_id=post_obj.id))
    elif request.method == "GET":
        form.title.data = post_obj.title
        form.content.data = post_obj.content

    return render_template("create_post.html", title="Update Post", form=form, legend="Update Post")


@posts.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    if post_obj.author != current_user:
        abort(403)
    db.session.delete(post_obj)
    db.session.commit()
    flash("Your post has been deleted.", "danger")
    return redirect(url_for("main.home"))