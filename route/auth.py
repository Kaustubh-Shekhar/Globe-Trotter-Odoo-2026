from flask import Blueprint, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User
from helpers import pick_image

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _unique_username(preferred, email):
    """Use what the user typed; fall back to the email local-part. Always unique."""
    base = (preferred or "").strip().lower()
    if not base:
        base = email.split("@")[0].strip().lower()
    base = "".join(ch for ch in base if ch.isalnum() or ch in "._-")[:40] or "traveller"

    candidate, n = base, 1
    while User.query.filter_by(username=candidate).first():
        n += 1
        candidate = f"{base}{n}"
    return candidate


def _back_to_register(message):
    flash(message, "error")
    # the #register fragment makes auth.js reopen the registration view
    return redirect(url_for("home") + "#register")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    first_name = (request.form.get("first_name") or "").strip()
    last_name = (request.form.get("last_name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    phone = (request.form.get("phone") or "").strip()
    city = (request.form.get("city") or "").strip()
    country = (request.form.get("country") or "").strip()
    # an uploaded file wins; a pasted URL still works as a fallback
    photo = pick_image(request.files.get("photo_file"), request.form.get("photo"))
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirmPassword") or ""

    if not first_name or not last_name or not email or not password:
        return _back_to_register("First name, last name, email and password are required.")

    if password != confirm:
        return _back_to_register("Passwords do not match.")

    if len(password) < 8:
        return _back_to_register("Password must be at least 8 characters.")

    if User.query.filter_by(email=email).first():
        return _back_to_register("That email is already registered. Try logging in.")

    if username and User.query.filter_by(username=username).first():
        return _back_to_register(f'The username "{username}" is taken.')

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone or None,
        city=city or None,
        country=country or None,
        photo=photo,
        username=_unique_username(username, email),
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    flash(f"Welcome aboard, {user.first_name}! You are signed in as {user.username}.", "success")
    return redirect(url_for("trips.dashboard"))


@auth_bp.route("/login", methods=["POST"])
def login():
    # screen 1 asks for a username, but accepting the email too costs nothing
    identifier = (request.form.get("username") or request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    user = User.query.filter_by(username=identifier).first()
    if user is None:
        user = User.query.filter_by(email=identifier).first()

    if user is None or not check_password_hash(user.password_hash, password):
        flash("Invalid username or password.", "error")
        return redirect(url_for("home"))

    session["user_id"] = user.id
    flash(f"Welcome back, {user.first_name}!", "success")
    return redirect(url_for("trips.dashboard"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))
