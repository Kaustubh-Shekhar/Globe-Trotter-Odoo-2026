# GlobeTrotter

A personalised multi-city travel planner for **Indian destinations**. Build a trip,
add cities as stops, attach activities and costs to each stop, watch the budget
update, and share the finished itinerary via a public link that anyone can copy
into their own account.

Odoo Hackathon 2026 — built by Kaustubh Shekhar and Shlok.

---

## Run it

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python app.py
```

Open <http://127.0.0.1:5000> and log in with **`demo` / `demo1234`**.

> `seed.py` drops and recreates every table. Re-run it after any model change —
> `db.create_all()` does not alter existing tables.

Seeded data: **32 Indian cities across 19 states**, 87 activities, and a demo
"Golden Triangle 2026" trip (Delhi → Agra → Jaipur, 10 days, ₹54,950).

---

## The schema

Six tables. The interesting parts are the two rules that keep the money correct.

```
users ──< trips ──< stops ──< trip_activities >── activities >── cities
                 └─< expenses ──┘                              (state, country)
```

| Table | Holds |
|---|---|
| `users` | account + profile (name, email, phone, home city/country) |
| `cities` | destination catalogue — name, **state**, country, lat/lon, cost_index, popularity |
| `activities` | the master catalogue of things to do, owned by a city |
| `trips` | a plan owned by a user, optionally public via `share_token` |
| `stops` | a city within a trip, ordered by `position` |
| `trip_activities` | an activity scheduled at a stop, on a date |
| `expenses` | transport / accommodation / food / other, attached to a trip and a stop |

### Snapshotting

`trip_activities` stores its **own `name` and `cost`** rather than only pointing at
`activities`. Two reasons:

1. A saved plan must not silently change when the master catalogue price moves.
2. `activity_id` is nullable, so a user can add a custom activity that exists
   nowhere in the catalogue.

### One source of truth for money

Activity money lives in `trip_activities.cost`. Everything else lives in
`expenses`, which may only carry `Transport`, `Accommodation`, `Food` or `Other`
— **never `Activities`**. The category is validated server-side, so the budget
cannot double-count. `compute_budget()` in `route/budget.py` is the single
function behind both the budget page and the JSON API, so the chart and the
tables can never disagree.

### Copy Trip

`POST /share/<token>/copy` deep-copies a shared trip into the viewer's account:
one transaction across `trips`, `stops`, `trip_activities` and `expenses`.
`db.session.flush()` assigns primary keys before the child rows reference them,
and an `old_stop_id → new_stop_id` map re-points each expense at the copy's own
stops instead of leaving it attached to the original's.

---

## Screens

| Screen | Route |
|---|---|
| Login / Registration | `/` |
| Dashboard — search + filter by state | `/dashboard` |
| My Trips — grouped Ongoing / Up-coming / Completed | `/trips` |
| Create Trip | `/trips/new` |
| Itinerary Builder | `/trips/<id>/build` |
| Itinerary View — day by day | `/trips/<id>/view` |
| Budget & Cost Breakdown | `/trips/<id>/budget` |
| Public Shared Itinerary + Copy Trip | `/share/<token>` |

## Stack

Flask + Flask-SQLAlchemy + SQLite, server-rendered Jinja2 templates, vanilla
CSS and JS. Every interaction is a form POST → redirect → flash. The single
exception is `/api/trips/<id>/budget`, which feeds the Chart.js doughnut.
