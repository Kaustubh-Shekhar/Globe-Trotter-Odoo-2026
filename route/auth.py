from flask import (Blueprint, request, redirect, url_for,
                   flash, session, render_template)
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _make_username(email):
    """Derive a unique username from the email local-part."""
    base = email.split("@")[0].strip().lower() or "traveller"
    base = "".join(ch for ch in base if ch.isalnum() or ch in "._-")[:40] or "traveller"
    candidate, n = base, 1
    while User.query.filter_by(username=candidate).first():
        n += 1
        candidate = f"{base}{n}"
    return candidate


@auth_bp.route("/signup", methods=["POST"])
def signup():
    full_name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirmPassword") or ""

    if not full_name or not email or not password:
        flash("Please fill in every field.", "error")
        return redirect(url_for("home"))

    if password != confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for("home"))

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect(url_for("home"))

    if User.query.filter_by(email=email).first():
        flash("That email is already registered. Try logging in.", "error")
        return redirect(url_for("home"))

    parts = full_name.split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else "-"

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=_make_username(email),
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    flash(f"Welcome aboard, {user.first_name}!", "success")
    return redirect(url_for("trips.dashboard"))


@auth_bp.route("/login", methods=["POST"])
def login():
    identifier = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    # allow logging in with either email or username (the demo user is "demo")
    user = User.query.filter_by(email=identifier).first()
    if user is None:
        user = User.query.filter_by(username=identifier).first()

    if user is None or not check_password_hash(user.password_hash, password):
        flash("Invalid email or password.", "error")
        return redirect(url_for("home"))

    session["user_id"] = user.id
    flash(f"Welcome back, {user.first_name}!", "success")
    return redirect(url_for("trips.dashboard"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))
