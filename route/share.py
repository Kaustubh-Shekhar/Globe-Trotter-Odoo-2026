import secrets

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, abort, request)

from extensions import db
from models import Trip, Stop, TripActivity, Expense, User
from helpers import login_required, current_user

share_bp = Blueprint("share", __name__)


def _owned_trip(trip_id):
    trip = Trip.query.get(trip_id)
    if trip is None:
        abort(404)
    user = current_user()
    if user is None or trip.user_id != user.id:
        abort(403)
    return trip


def _stop_total(trip, stop):
    acts = sum(ta.cost or 0 for ta in stop.trip_activities)
    exps = sum(e.amount or 0 for e in trip.expenses if e.stop_id == stop.id)
    return acts + exps


@share_bp.route("/trips/<int:trip_id>/share", methods=["POST"])
@login_required
def make_public(trip_id):
    trip = _owned_trip(trip_id)

    if request.form.get("action") == "unpublish":
        trip.is_public = False
        db.session.commit()
        flash("This itinerary is private again.", "info")
        return redirect(url_for("itinerary.view_trip", trip_id=trip.id))

    if not trip.share_token:
        # token_urlsafe(12) is 16 chars — comfortably inside share_token's 40
        trip.share_token = secrets.token_urlsafe(12)

    trip.is_public = True
    db.session.commit()

    flash("Public link is live. Anyone with the link can view this trip.", "success")
    return redirect(url_for("itinerary.view_trip", trip_id=trip.id))


@share_bp.route("/share/<token>")
def public_view(token):
    """No @login_required — this is the whole point of a share link."""
    trip = Trip.query.filter_by(share_token=token).first()
    if trip is None or not trip.is_public:
        abort(404)

    owner = User.query.get(trip.user_id)
    owner_name = f"{owner.first_name} {owner.last_name}".strip() if owner else "a traveller"

    stop_totals = {s.id: _stop_total(trip, s) for s in trip.stops}
    grand_total = sum(stop_totals.values())
    stop_expenses = {s.id: [e for e in trip.expenses if e.stop_id == s.id]
                     for s in trip.stops}

    return render_template("shared.html", trip=trip, stops=trip.stops,
                           owner_name=owner_name, stop_totals=stop_totals,
                           stop_expenses=stop_expenses, grand_total=grand_total,
                           viewer=current_user())


@share_bp.route("/share/<token>/copy", methods=["POST"])
@login_required
def copy_trip(token):
    """Deep-copy a shared trip into the signed-in user's account.

    One transaction, four tables: trips -> stops -> trip_activities, plus
    expenses which point at both the trip and a stop. The flush() calls matter:
    they assign primary keys so the child rows have something to point at
    without committing a half-built trip.
    """
    source = Trip.query.filter_by(share_token=token).first()
    if source is None or not source.is_public:
        abort(404)

    user = current_user()

    if source.user_id == user.id:
        flash("This trip is already yours.", "info")
        return redirect(url_for("itinerary.view_trip", trip_id=source.id))

    copy = Trip(
        user_id=user.id,
        name=f"{source.name} (copy)",
        description=source.description,
        start_date=source.start_date,
        end_date=source.end_date,
        cover_image=source.cover_image,
        is_public=False,      # a copy starts private, with no token of its own
        share_token=None,
    )
    db.session.add(copy)
    db.session.flush()

    # old stop id -> new stop id, so expenses can be re-pointed correctly
    stop_id_map = {}

    for stop in source.stops:
        new_stop = Stop(
            trip_id=copy.id,
            city_id=stop.city_id,
            start_date=stop.start_date,
            end_date=stop.end_date,
            position=stop.position,
        )
        db.session.add(new_stop)
        db.session.flush()
        stop_id_map[stop.id] = new_stop.id

        for ta in stop.trip_activities:
            # the snapshot travels with the copy, so the copied plan keeps the
            # price it was planned at even if the catalogue moves
            db.session.add(TripActivity(
                stop_id=new_stop.id,
                activity_id=ta.activity_id,
                name=ta.name,
                cost=ta.cost,
                date=ta.date,
                position=ta.position,
            ))

    for expense in source.expenses:
        db.session.add(Expense(
            trip_id=copy.id,
            stop_id=stop_id_map.get(expense.stop_id),
            category=expense.category,
            amount=expense.amount,
            description=expense.description,
        ))

    db.session.commit()

    flash(f'Copied "{source.name}" into your trips. Make it your own.', "success")
    return redirect(url_for("itinerary.builder", trip_id=copy.id))
