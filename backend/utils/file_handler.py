"""
utils/file_handler.py
Safe, reusable upload handling: validates extension, generates a unique
filename (avoids overwrites/collisions), and saves to the right folder.
"""

import os
import uuid
from werkzeug.utils import secure_filename


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def save_upload(file_storage, folder: str, allowed_extensions: set) -> str:
    """
    Validates and saves an uploaded file.
    Returns the relative path stored in the DB (e.g. 'uploads/images/abc123.jpg').
    Raises ValueError if the file type isn't allowed.
    """
    filename = file_storage.filename
    if not filename or not allowed_file(filename, allowed_extensions):
        raise ValueError(
            f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    ext = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    safe_name = secure_filename(unique_name)

    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, safe_name)
    file_storage.save(full_path)

    return full_path
