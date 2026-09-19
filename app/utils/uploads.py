"""Secure reference-image uploads (master prompt §16/§51/§62).

Every upload is checked by extension *and* by actually decoding it as an
image (Pillow) before it touches disk, stored under a random filename
outside anything served directly, and never executed.
"""
from __future__ import annotations

import os
import secrets
from io import BytesIO

from flask import current_app
from flask_babel import gettext as _

_MIME_BY_FORMAT = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class UploadError(ValueError):
    """Raised for a rejected upload — safe to show to the user verbatim."""


def save_reference_image(file_storage) -> dict:
    filename = (file_storage.filename or "").strip()
    if not filename:
        raise UploadError(_("Please choose a file."))

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed_ext = current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    if ext not in allowed_ext:
        raise UploadError(_("Only JPG, PNG or WEBP images are allowed."))

    data = file_storage.read()
    if not data:
        raise UploadError(_("That file is empty."))
    if len(data) > current_app.config["MAX_CONTENT_LENGTH"]:
        raise UploadError(_("That image is too large."))

    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:  # pragma: no cover - Pillow is a hard dependency
        raise UploadError(_("Image support is not available.")) from exc

    try:
        img = Image.open(BytesIO(data))
        img.verify()
        detected_format = img.format
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise UploadError(_("That file doesn't look like a valid image.")) from exc

    mime_type = _MIME_BY_FORMAT.get(detected_format or "")
    if mime_type not in current_app.config["ALLOWED_IMAGE_MIME_TYPES"]:
        raise UploadError(_("Unsupported image type."))

    upload_dir = current_app.config["UPLOAD_DIR"]
    os.makedirs(upload_dir, exist_ok=True)
    random_name = f"{secrets.token_hex(16)}.{ext}"
    with open(os.path.join(upload_dir, random_name), "wb") as fh:
        fh.write(data)

    return {
        "file_name": filename[:255],
        "storage_path": random_name,
        "mime_type": mime_type,
        "file_size": len(data),
    }


def upload_path(storage_path: str) -> str:
    return os.path.join(current_app.config["UPLOAD_DIR"], storage_path)
