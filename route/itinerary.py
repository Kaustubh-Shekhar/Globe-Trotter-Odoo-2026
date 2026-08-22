from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort)

from extensions import db
from models import Trip, Stop, City, Activity, TripActivity, Expense
from helpers import login_required, current_user, parse_date

itinerary_bp = Blueprint("itinerary", __name__)

# RULE 5: an Expense row may never carry "Activities" — activity money lives on
# TripActivity.cost. Anything else here would double-count in the budget.
EXPENSE_CATEGORIES = ("Transport", "Accommodation", "Food", "Other")


def _owned_trip(trip_id):
    trip = Trip.query.get(trip_id)
    if trip is None:
        abort(404)
    user = current_user()
    if user is None or trip.user_id != user.id:
        abort(403)
    return trip


def _owned_stop(stop_id):
    stop = Stop.query.get(stop_id)
    if stop is None:
        abort(404)
    user = current_user()
    if user is None or stop.trip.user_id != user.id:
        abort(403)
    return stop


def _stop_total(stop):
    acts = sum(ta.cost or 0 for ta in stop.trip_activities)
    exps = sum(e.amount or 0 for e in stop.trip.expenses if e.stop_id == stop.id)
    return acts + exps


def _resequence(trip):
    """Rewrite positions as 0,1,2... so ordering stays stable after a delete."""
    for i, stop in enumerate(sorted(trip.stops, key=lambda s: s.position)):
        stop.position = i


# =====================================================================
# SCREEN 5 — itinerary builder
# =====================================================================

@itinerary_bp.route("/trips/<int:trip_id>/build")
@login_required
def builder(trip_id):
    trip = _owned_trip(trip_id)
    stops = trip.stops
    cities = City.query.order_by(City.name.asc()).all()

    # activity catalogue for each city on the trip, for the add-activity picker
    activities = {}
    for stop in stops:
        if stop.city_id not in activities:
            activities[stop.city_id] = (Activity.query
                                        .filter_by(city_id=stop.city_id)
                                        .order_by(Activity.name.asc()).all())

    stop_totals = {s.id: _stop_total(s) for s in stops}
    stop_expenses = {s.id: [e for e in trip.expenses if e.stop_id == s.id]
                     for s in stops}

    return render_template("builder.html", trip=trip, stops=stops,
                           cities=cities, activities=activities,
                           stop_totals=stop_totals, stop_expenses=stop_expenses,
                           categories=EXPENSE_CATEGORIES)


@itinerary_bp.route("/trips/<int:trip_id>/stops/add", methods=["POST"])
@login_required
def add_stop(trip_id):
    trip = _owned_trip(trip_id)

    city_id = request.form.get("city_id", type=int)
    if not city_id or City.query.get(city_id) is None:
        flash("Pick a city to add.", "error")
        return redirect(url_for("itinerary.builder", trip_id=trip.id))

    start_date = parse_date(request.form.get("start_date")) or trip.start_date
    end_date = parse_date(request.form.get("end_date")) or trip.end_date

    if start_date and end_date and end_date < start_date:
        flash("That stop ends before it starts.", "error")
        return redirect(url_for("itinerary.builder", trip_id=trip.id))

    next_position = max([s.position for s in trip.stops], default=-1) + 1

    stop = Stop(trip_id=trip.id, city_id=city_id, start_date=start_date,
                end_date=end_date, position=next_position)
    db.session.add(stop)
    db.session.commit()

    flash(f"Added {stop.city.name} to the itinerary.", "success")
    return redirect(url_for("itinerary.builder", trip_id=trip.id))


@itinerary_bp.route("/stops/<int:stop_id>/delete", methods=["POST"])
@login_required
def delete_stop(stop_id):
    stop = _owned_stop(stop_id)
    trip = stop.trip
    name = stop.city.name if stop.city else "That stop"

    # expenses point at a stop but cascade from the trip, so clear them by hand
    Expense.query.filter_by(stop_id=stop.id).delete()
    db.session.delete(stop)
    db.session.flush()
    _resequence(trip)
    db.session.commit()

    flash(f"Removed {name}.", "info")
    return redirect(url_for("itinerary.builder", trip_id=trip.id))


@itinerary_bp.route("/stops/<int:stop_id>/move", methods=["POST"])
@login_required
def move_stop(stop_id):
    stop = _owned_stop(stop_id)
    trip = stop.trip
    direction = request.form.get("direction")

    ordered = sorted(trip.stops, key=lambda s: s.position)
    index = ordered.index(stop)
    swap_with = index - 1 if direction == "up" else index + 1

    if 0 <= swap_with < len(ordered):
        other = ordered[swap_with]
        stop.position, other.position = other.position, stop.position
        db.session.commit()

    return redirect(url_for("itinerary.builder", trip_id=trip.id))


# =====================================================================
# activities on a stop
# =====================================================================

@itinerary_bp.route("/stops/<int:stop_id>/activities/add", methods=["POST"])
@login_required
def add_activity(stop_id):
    stop = _owned_stop(stop_id)

    activity_id = request.form.get("activity_id", type=int)
    custom_name = (request.form.get("name") or "").strip()
    custom_cost = request.form.get("cost", type=float)
    when = parse_date(request.form.get("date")) or stop.start_date

    # RULE 4: name and cost are SNAPSHOT onto TripActivity. The saved plan must
    # not shift when the master catalogue price changes, and this is also what
    # lets a custom activity exist with activity_id = NULL.
    if activity_id:
        activity = Activity.query.get(activity_id)
        if activity is None or activity.city_id != stop.city_id:
            flash("That activity does not belong to this city.", "error")
            return redirect(url_for("itinerary.builder", trip_id=stop.trip_id))
        name = activity.name
        cost = activity.estimated_cost or 0
    elif custom_name:
        activity = None
        name = custom_name
        cost = custom_cost or 0
    else:
        flash("Pick an activity or type your own.", "error")
        return redirect(url_for("itinerary.builder", trip_id=stop.trip_id))

    next_position = max([ta.position for ta in stop.trip_activities], default=-1) + 1

    db.session.add(TripActivity(
        stop_id=stop.id,
        activity_id=activity.id if activity else None,
        name=name, cost=cost, date=when, position=next_position))
    db.session.commit()

    flash(f'Added "{name}".', "success")
    return redirect(url_for("itinerary.builder", trip_id=stop.trip_id))


@itinerary_bp.route("/trip_activities/<int:ta_id>/delete", methods=["POST"])
@login_required
def delete_activity(ta_id):
    ta = TripActivity.query.get(ta_id)
    if ta is None:
        abort(404)
    user = current_user()
    if user is None or ta.stop.trip.user_id != user.id:
        abort(403)

    trip_id = ta.stop.trip_id
    name = ta.name
    db.session.delete(ta)
    db.session.commit()

    flash(f'Removed "{name}".', "info")
    return redirect(url_for("itinerary.builder", trip_id=trip_id))


# =====================================================================
# expenses on a stop (Transport / Accommodation / Food / Other)
# =====================================================================

@itinerary_bp.route("/stops/<int:stop_id>/expenses/add", methods=["POST"])
@login_required
def add_expense(stop_id):
    stop = _owned_stop(stop_id)

    category = request.form.get("category")
    amount = request.form.get("amount", type=float)
    description = (request.form.get("description") or "").strip()

    if category not in EXPENSE_CATEGORIES:
        flash("Pick a valid expense category.", "error")
        return redirect(url_for("itinerary.builder", trip_id=stop.trip_id))

    if not amount or amount <= 0:
        flash("Enter an amount greater than zero.", "error")
        return redirect(url_for("itinerary.builder", trip_id=stop.trip_id))

    db.session.add(Expense(trip_id=stop.trip_id, stop_id=stop.id,
                           category=category, amount=amount,
                           description=description or None))
    db.session.commit()

    flash(f"Added {category} cost.", "success")
    return redirect(url_for("itinerary.builder", trip_id=stop.trip_id))


@itinerary_bp.route("/expenses/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense is None:
        abort(404)
    user = current_user()
    if user is None or expense.trip.user_id != user.id:
        abort(403)

    trip_id = expense.trip_id
    db.session.delete(expense)
    db.session.commit()

    flash("Expense removed.", "info")
    return redirect(url_for("itinerary.builder", trip_id=trip_id))


# =====================================================================
# SCREEN 9 — itinerary view, day by day
# =====================================================================

def build_timeline(trip):
    """Flatten stops into day cards: [{day, date, stop, activities, expenses}]."""
    timeline = []
    day_number = 0

    for stop in trip.stops:
        # bucket this stop's activities by the date they sit on
        by_date = {}
        for ta in stop.trip_activities:
            by_date.setdefault(ta.date or stop.start_date, []).append(ta)

        dates = sorted([d for d in by_date if d is not None])
        if not dates:
            dates = [stop.start_date]

        expenses = [e for e in trip.expenses if e.stop_id == stop.id]

        for i, day in enumerate(dates):
            day_number += 1
            timeline.append({
                "day": day_number,
                "date": day,
                "stop": stop,
                "first_of_stop": i == 0,
                "activities": by_date.get(day, []),
                # expenses hang off the stop, so show them on its first day
                "expenses": expenses if i == 0 else [],
            })

    return timeline


@itinerary_bp.route("/trips/<int:trip_id>/view")
@login_required
def view_trip(trip_id):
    trip = _owned_trip(trip_id)
    timeline = build_timeline(trip)
    stop_totals = {s.id: _stop_total(s) for s in trip.stops}
    grand_total = sum(stop_totals.values())

    return render_template("itinerary.html", trip=trip, stops=trip.stops,
                           timeline=timeline, stop_totals=stop_totals,
                           grand_total=grand_total)
