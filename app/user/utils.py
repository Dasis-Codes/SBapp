import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flask import current_app
from app import mail

def save_picture(form_picture, output_size=(125, 125)):
    """
    Save an uploaded picture (werkzeug FileStorage) to static/pics and return the filename.
    Converts to RGB to avoid issues with some file modes.
    """
    # ensure the upload folder exists
    upload_folder = os.path.join(current_app.root_path, "static", "pics")
    os.makedirs(upload_folder, exist_ok=True)

    random_hex = secrets.token_hex(8)
    # use secure_filename to avoid strange characters (we keep extension)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext.lower()
    picture_path = os.path.join(upload_folder, picture_fn)

    # Use PIL to open and thumbnail
    img = Image.open(form_picture)
    # Convert to RGB (handles PNG with alpha etc.)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for("user.reset_password", token=token, _external=True)

    msg = Message(
        "Password Reset Request",
        sender='s11smehar432@gmail.com',
        recipients=[user.email],  # no need to specify sender, uses MAIL_DEFAULT_SENDER
    )

    msg.body = f"""To reset your password, visit the following link:

{reset_url}

If you did not request this, simply ignore this email.
"""

    mail.send(msg)