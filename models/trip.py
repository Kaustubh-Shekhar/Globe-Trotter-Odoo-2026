from datetime import datetime
from extensions import db


class Trip(db.Model):
    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cover_image = db.Column(db.String(400))
    is_public = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(40), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(
        "User",
        backref=db.backref("trips", cascade="all, delete-orphan"))
    stops = db.relationship(
        "Stop", backref="trip", cascade="all, delete-orphan",
        order_by="Stop.position")
    expenses = db.relationship(
        "Expense", backref="trip", cascade="all, delete-orphan")

    @property
    def days(self):
        if self.start_date and self.end_date:
            return max((self.end_date - self.start_date).days, 1)
        return 1

    def __repr__(self):
        return f"<Trip {self.name}>"


class Stop(db.Model):
    __tablename__ = "stops"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    position = db.Column(db.Integer, default=0)

    city = db.relationship("City")
    trip_activities = db.relationship(
        "TripActivity", backref="stop", cascade="all, delete-orphan",
        order_by="TripActivity.position")

    @property
    def nights(self):
        if self.start_date and self.end_date:
            return max((self.end_date - self.start_date).days, 1)
        return 1


class TripActivity(db.Model):
    __tablename__ = "trip_activities"
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey("stops.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    name = db.Column(db.String(200), nullable=False)   # snapshot
    cost = db.Column(db.Float, default=0)              # snapshot
    date = db.Column(db.Date)
    position = db.Column(db.Integer, default=0)

    activity = db.relationship("Activity")


class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    stop_id = db.Column(db.Integer, db.ForeignKey("stops.id"))
    category = db.Column(db.String(40))   # Transport/Accommodation/Food/Other
    amount = db.Column(db.Float, default=0)
    description = db.Column(db.String(200))