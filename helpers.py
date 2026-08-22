from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for


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