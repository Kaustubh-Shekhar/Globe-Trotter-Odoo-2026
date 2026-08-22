from flask import Flask, render_template
from extensions import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "hackathon-dev-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///globetrotter.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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


@app.route("/")
def home():
    return render_template("auth.html")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
