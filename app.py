import os

from flask import Flask, render_template, url_for
from extensions import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "hackathon-dev-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///globetrotter.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# profile photos and trip covers are uploaded, so cap the request size.
# Flask raises 413 past this; see the handler below.
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024   # 4 MB
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

import models  # noqa: F401  — registers all tables before create_all


def register_if_ready(module_name, bp_name):
    """Register a blueprint only if its file actually defines one yet.

    Two people are pushing route files at different times. Without this, one
    empty file on main crashes the app for BOTH of us. Missing routes just
    404 instead of taking the whole server down.
    """
    try:
        module = __import__(module_name, fromlist=[bp_name])
        app.register_blueprint(getattr(module, bp_name))
        print(f"  [ok]      {module_name}.{bp_name}")
    except (ImportError, AttributeError) as e:
        print(f"  [pending] {module_name}.{bp_name} -> {e}")


print("registering blueprints:")
register_if_ready("route.auth", "auth_bp")
register_if_ready("route.trips", "trips_bp")
register_if_ready("route.budget", "budget_bp")
register_if_ready("route.itinerary", "itinerary_bp")
register_if_ready("route.share", "share_bp")
register_if_ready("route.profile", "profile_bp")


@app.errorhandler(413)
def too_large(_e):
    """A file over MAX_CONTENT_LENGTH would otherwise show a bare 413 page."""
    from flask import flash, request, redirect
    flash("That image is too large — keep it under 4 MB.", "error")
    return redirect(request.referrer or url_for("home")), 302


@app.context_processor
def inject_nav_user():
    """Makes the logged-in user available to every template (base.html avatar)
    without each blueprint having to pass it in."""
    from helpers import current_user
    user = current_user()
    initials = "?"
    if user:
        first = (user.first_name or "")[:1]
        last = (user.last_name or "")[:1]
        if last == "-":
            last = ""
        initials = (first + last).upper() or "?"
    return {"nav_user": user, "nav_initials": initials}


@app.route("/")
def home():
    return render_template("auth.html")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    # honours PORT when something else already holds 5000; plain
    # `python app.py` still comes up on the usual http://127.0.0.1:5000
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
