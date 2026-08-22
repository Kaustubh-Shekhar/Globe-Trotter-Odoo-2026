from flask import Blueprint, render_template

from models import City, Trip
from helpers import login_required, current_user

trips_bp = Blueprint("trips", __name__)


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
