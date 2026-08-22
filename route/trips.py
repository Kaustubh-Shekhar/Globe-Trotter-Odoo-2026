from datetime import date

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


def trip_status(trip):
    """Ongoing / Up-coming / Completed — the groups on the trip listing screen."""
    today = date.today()
    if not trip.start_date or not trip.end_date:
        return "Undated"
    if trip.start_date <= today <= trip.end_date:
        return "Ongoing"
    if trip.start_date > today:
        return "Up-coming"
    return "Completed"


@trips_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    q = (request.args.get("q") or "").strip()
    sort = request.args.get("sort") or "popularity"

    trips = (Trip.query
             .filter_by(user_id=user.id)
             .order_by(Trip.created_at.desc())
             .limit(3).all())

    country = (request.args.get("country") or "").strip()

    cities = City.query
    if q:
        like = f"%{q}%"
        # search the state as well, so "Kerala" or "Rajasthan" finds cities
        cities = cities.filter(db.or_(City.name.ilike(like),
                                      City.state.ilike(like),
                                      City.country.ilike(like)))
    if country:
        cities = cities.filter(City.country == country)

    if sort == "name":
        cities = cities.order_by(City.name.asc())
    elif sort == "cost_low":
        cities = cities.order_by(City.cost_index.asc(), City.popularity.desc())
    elif sort == "cost_high":
        cities = cities.order_by(City.cost_index.desc(), City.popularity.desc())
    else:
        cities = cities.order_by(City.popularity.desc())

    popular_cities = cities.limit(12).all()

    # distinct country list for the Filter dropdown
    countries = [row[0] for row in
                 db.session.query(City.country).distinct().order_by(City.country).all()]

    return render_template("dashboard.html", user=user, trips=trips,
                           popular_cities=popular_cities, q=q, sort=sort,
                           country=country, countries=countries)


@trips_bp.route("/trips")
@login_required
def my_trips():
    user = current_user()
    q = (request.args.get("q") or "").strip()
    group = request.args.get("group") or "status"
    status_filter = request.args.get("filter") or "all"
    sort = request.args.get("sort") or "start"

    query = Trip.query.filter_by(user_id=user.id)

    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Trip.name.ilike(like),
                                    Trip.description.ilike(like)))

    if sort == "name":
        query = query.order_by(Trip.name.asc())
    elif sort == "created":
        query = query.order_by(Trip.created_at.desc())
    else:
        query = query.order_by(Trip.start_date.is_(None), Trip.start_date.asc())

    trips = query.all()

    if status_filter != "all":
        trips = [t for t in trips if trip_status(t) == status_filter]

    # build the grouped view the wireframe shows
    if group == "none":
        groups = [("All trips", trips)]
    else:
        buckets = {"Ongoing": [], "Up-coming": [], "Completed": [], "Undated": []}
        for t in trips:
            buckets[trip_status(t)].append(t)
        groups = [(name, rows) for name, rows in buckets.items() if rows]

    return render_template("trips.html", trips=trips, groups=groups,
                           q=q, group=group, status_filter=status_filter,
                           sort=sort, trip_status=trip_status)


@trips_bp.route("/trips/new", methods=["GET", "POST"])
@login_required
def create_trip():
    suggestions = City.query.order_by(City.popularity.desc()).limit(6).all()

    if request.method == "GET":
        return render_template("createTrip.html", error=None, suggestions=suggestions)

    user = current_user()
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    cover_image = (request.form.get("cover_image") or "").strip()
    start_date = parse_date(request.form.get("start_date"))
    end_date = parse_date(request.form.get("end_date"))

    if not name:
        return render_template("createTrip.html",
                               error="Give your trip a name.",
                               suggestions=suggestions)

    if start_date and end_date and end_date < start_date:
        return render_template("createTrip.html",
                               error="The end date cannot be before the start date.",
                               suggestions=suggestions)

    trip = Trip(user_id=user.id, name=name, description=description,
                start_date=start_date, end_date=end_date,
                cover_image=cover_image or None)
    db.session.add(trip)
    db.session.commit()

    flash(f'"{trip.name}" created. Now add some cities.', "success")
    # literal path: itinerary_bp lands later, and url_for would BuildError
    # until it does. This URL is correct either way.
    return redirect(f"/trips/{trip.id}/build")


@trips_bp.route("/trips/<int:trip_id>/delete", methods=["POST"])
@login_required
def delete_trip(trip_id):
    trip = _owned_trip(trip_id)
    name = trip.name
    # cascades wipe stops -> trip_activities and expenses in one transaction
    db.session.delete(trip)
    db.session.commit()
    flash(f'"{name}" was deleted.', "info")
    return redirect(url_for("trips.my_trips"))
