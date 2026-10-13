from io import BytesIO
from uuid import uuid4

from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

ALLOWED_TYPES = ["JPEG", "JPG", "PNG", "WEBP"]
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    if ext not in ALLOWED_TYPES:
        ext = 'jpg'
    return f"avatars/{uuid4()}.{ext}"

def validate_avatar(file):
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("file size must be less than 2 MB")

    try:
        img = Image.open(file)
        img.verify()
    except (OSError, UnidentifiedImageError):
        raise ValidationError("Invalid image file")
    finally:
        file.seek(0)

    # check file format
    img = Image.open(file)
    if img.format not in ALLOWED_TYPES:
        raise ValidationError("Only JPEG, JPG, PNG, WEBP allowed")

    # check file dimension
    width, height = img.size
    if width > 1000 or height > 1000:
        raise ValidationError("Image is too large")

    file.seek(0)

def process_image(file):
    try:
        img = Image.open(file)

        # check color's image
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # change file size
        img.thumbnail((512, 512))

        # save image bytes on RAM
        output = BytesIO()
        img.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)
        filename = f"{uuid4()}.jpg"
        # convert byte to image
        return ContentFile(output.getvalue(), name=filename)

    except Exception as e:
        raise ValidationError(f"Failed to process image :{str(e)}")
