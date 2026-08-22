from flask import Blueprint, render_template, jsonify, abort

from models import Trip
from helpers import login_required, current_user

budget_bp = Blueprint("budget", __name__)

# RULE 5: the ONLY categories an Expense row may hold. Activity money comes
# from TripActivity.cost and nowhere else. Anything unexpected is folded into
# "Other" rather than trusted, so a stray row can never double-count.
EXPENSE_CATEGORIES = ("Transport", "Accommodation", "Food", "Other")


def _owned_trip(trip_id):
    trip = Trip.query.get(trip_id)
    if trip is None:
        abort(404)
    user = current_user()
    if user is None or trip.user_id != user.id:
        abort(403)
    return trip


def compute_budget(trip):
    """Single source of truth for trip money. Used by both the page and the API."""
    by_category = {"Activities": 0.0, "Accommodation": 0.0,
                   "Transport": 0.0, "Food": 0.0, "Other": 0.0}

    for stop in trip.stops:
        for ta in stop.trip_activities:
            by_category["Activities"] += ta.cost or 0

    for e in trip.expenses:
        cat = e.category if e.category in EXPENSE_CATEGORIES else "Other"
        by_category[cat] += e.amount or 0

    total = sum(by_category.values())
    days = trip.days
    per_day = round(total / days, 2) if days else 0.0

    per_stop = []
    for stop in trip.stops:
        acts = sum(ta.cost or 0 for ta in stop.trip_activities)
        exps = sum(e.amount or 0 for e in trip.expenses if e.stop_id == stop.id)
        per_stop.append({
            "stop_id": stop.id,
            "city": stop.city.name if stop.city else "Unknown",
            "country": stop.city.country if stop.city else "",
            "nights": stop.nights,
            "activities": round(acts, 2),
            "expenses": round(exps, 2),
            "total": round(acts + exps, 2),
        })

    return {
        "total": round(total, 2),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "per_day": per_day,
        "days": days,
        "per_stop": per_stop,
    }


@budget_bp.route("/trips/<int:trip_id>/budget")
@login_required
def budget_page(trip_id):
    trip = _owned_trip(trip_id)
    data = compute_budget(trip)
    return render_template("budget.html", trip=trip, **data)


@budget_bp.route("/api/trips/<int:trip_id>/budget")
@login_required
def budget_json(trip_id):
    trip = _owned_trip(trip_id)
    return jsonify(compute_budget(trip))
