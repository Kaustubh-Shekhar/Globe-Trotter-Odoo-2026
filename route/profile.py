from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash

from extensions import db
from models import Trip, User
from helpers import login_required, current_user, pick_image

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    user = current_user()
    today = date.today()

    trips = (Trip.query
             .filter_by(user_id=user.id)
             .order_by(Trip.start_date.is_(None), Trip.start_date.asc())
             .all())

    # screen 7 splits the user's trips into what is still ahead and what is done
    preplanned = [t for t in trips
                  if not t.end_date or t.end_date >= today]
    previous = [t for t in trips
                if t.end_date and t.end_date < today]

    return render_template("profile.html", user=user,
                           preplanned=preplanned, previous=previous)


@profile_bp.route("/profile/edit", methods=["POST"])
@login_required
def update_profile():
    user = current_user()

    first_name = (request.form.get("first_name") or "").strip()
    last_name = (request.form.get("last_name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()

    if not first_name or not last_name or not email:
        flash("First name, last name and email are required.", "error")
        return redirect(url_for("profile.profile"))

    clash = User.query.filter(User.email == email, User.id != user.id).first()
    if clash:
        flash("Another account already uses that email.", "error")
        return redirect(url_for("profile.profile"))

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.phone = (request.form.get("phone") or "").strip() or None
    user.city = (request.form.get("city") or "").strip() or None
    user.country = (request.form.get("country") or "").strip() or None

    # an uploaded file wins; a pasted URL is the fallback; blank keeps the old one
    new_photo = pick_image(request.files.get("photo_file"),
                           request.form.get("photo"))
    if new_photo:
        user.photo = new_photo

    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for("profile.profile"))


@profile_bp.route("/profile/photo/remove", methods=["POST"])
@login_required
def remove_photo():
    user = current_user()
    user.photo = None
    db.session.commit()
    flash("Photo removed.", "info")
    return redirect(url_for("profile.profile"))
