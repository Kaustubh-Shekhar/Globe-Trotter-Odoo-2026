from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort)

from extensions import db
from models import City, Trip
from helpers import login_required, current_user, parse_date

trips_bp = Blueprint("trips", __name__)


def _owned_trip(trip_id):
    trip = Trip.query.get(trip_id)
    if trip is None:
        abort(404)
    user = current_user()
    if user is None or trip.user_id != user.id:
        abort(403)
    return trip


@trips_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    trips = (Trip.query
             .filter_by(user_id=user.id)
             .order_by(Trip.created_at.desc())
             .limit(6).all())
    popular_cities = (City.query
                      .order_by(City.popularity.desc())
                      .limit(6).all())
    return render_template("dashboard.html", user=user,
                           trips=trips, popular_cities=popular_cities)


@trips_bp.route("/trips")
@login_required
def my_trips():
    user = current_user()
    trips = (Trip.query
             .filter_by(user_id=user.id)
             .order_by(Trip.start_date.is_(None), Trip.start_date.asc())
             .all())
    return render_template("trips.html", trips=trips)


@trips_bp.route("/trips/new", methods=["GET", "POST"])
@login_required
def create_trip():
    if request.method == "GET":
        return render_template("createTrip.html", error=None)

    user = current_user()
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    cover_image = (request.form.get("cover_image") or "").strip()
    start_date = parse_date(request.form.get("start_date"))
    end_date = parse_date(request.form.get("end_date"))

    if not name:
        return render_template("createTrip.html",
                               error="Give your trip a name.")

    if start_date and end_date and end_date < start_date:
        return render_template("createTrip.html",
                               error="The end date cannot be before the start date.")

    trip = Trip(user_id=user.id, name=name, description=description,
                start_date=start_date, end_date=end_date,
                cover_image=cover_image or None)
    db.session.add(trip)
    db.session.commit()

    flash(f"\"{trip.name}\" created. Now add some cities.", "success")
    # literal path: itinerary_bp lands in the next slot, and url_for would
    # BuildError until it does. This URL is correct either way.
    return redirect(f"/trips/{trip.id}/build")


@trips_bp.route("/trips/<int:trip_id>/delete", methods=["POST"])
@login_required
def delete_trip(trip_id):
    trip = _owned_trip(trip_id)
    name = trip.name
    # cascades wipe stops -> trip_activities and expenses in one transaction
    db.session.delete(trip)
    db.session.commit()
    flash(f"\"{name}\" was deleted.", "info")
    return redirect(url_for("trips.my_trips"))
