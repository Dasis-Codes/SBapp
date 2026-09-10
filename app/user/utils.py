import base64
from bs4 import BeautifulSoup
import io 
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

def process_embedded_images(html_content, max_size=(1200, 1200)):
    """
    Parses HTML content, finds base64 encoded <img> tags, converts them to compressed image files,
    saves them in static/pics, and returns the updated HTML content with file paths.
    """
    if not html_content:
        return html_content

    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')

    upload_folder = os.path.join(current_app.root_path, "static", "pics")
    os.makedirs(upload_folder, exist_ok=True)

    for img in images:
        src = img.get('src', '')
        # Check if the image source is a base64 string
        if src.startswith('data:image/'):
            try:
                # Extract header and base64 data
                header, encoded = src.split(',', 1)
                image_data = base64.b64decode(encoded)

                # Open with Pillow
                image = Image.open(io.BytesIO(image_data))
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Resize image to save memory and space
                image.thumbnail(max_size)

                # Generate a unique filename
                random_hex = secrets.token_hex(8)
                filename = f"{random_hex}.jpg"
                filepath = os.path.join(upload_folder, filename)

                # Save compressed JPEG image
                image.save(filepath, 'JPEG', quality=85)

                # Replace the giant Base64 src with the static file URL
                img['src'] = f"/static/pics/{filename}"
            except Exception as e:
                # If conversion fails for any reason, keep existing src or log error
                print(f"Error processing image: {e}")
                continue

    return str(soup)