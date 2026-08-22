import os
import secrets
from datetime import datetime
from functools import wraps

from flask import session, redirect, url_for, current_app
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
UPLOAD_SUBDIR = os.path.join("static", "uploads")


def parse_date(s):
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper


def current_user():
    from models import User
    if "user_id" not in session:
        return None
    return User.query.get(session["user_id"])


def save_image(file_storage):
    """Save an uploaded image and return the URL to serve it from.

    Returns None when nothing usable was uploaded (no file chosen, wrong
    extension) so callers can fall back to a pasted URL instead. The stored
    filename is random — never the user's, which could collide or escape the
    upload directory.
    """
    if file_storage is None or not file_storage.filename:
        return None

    original = secure_filename(file_storage.filename)
    if "." not in original:
        return None

    ext = original.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None

    folder = os.path.join(current_app.root_path, UPLOAD_SUBDIR)
    os.makedirs(folder, exist_ok=True)

    name = f"{secrets.token_hex(8)}.{ext}"
    file_storage.save(os.path.join(folder, name))

    return url_for("static", filename=f"uploads/{name}")


def pick_image(file_storage, pasted_url):
    """An uploaded file wins; otherwise fall back to a pasted URL."""
    uploaded = save_image(file_storage)
    if uploaded:
        return uploaded
    pasted = (pasted_url or "").strip()
    return pasted or None
