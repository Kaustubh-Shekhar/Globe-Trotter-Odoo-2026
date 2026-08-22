from extensions import db


class City(db.Model):
    __tablename__ = "cities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    # state / province. Nullable — only filled in where it is meaningful
    # (every Indian city has one; most single-region destinations do not).
    state = db.Column(db.String(120))
    country = db.Column(db.String(120), nullable=False)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    cost_index = db.Column(db.Integer, default=3)    # 1 cheap .. 5 luxury
    popularity = db.Column(db.Integer, default=50)   # 0..100
    image_url = db.Column(db.String(400))

    activities = db.relationship(
        "Activity", backref="city", cascade="all, delete-orphan")

    @property
    def region(self):
        """'Jaipur, Rajasthan, India' — or 'Paris, France' where there is no state."""
        parts = [self.state, self.country]
        return ", ".join(p for p in parts if p)

    def __repr__(self):
        return f"<City {self.name}>"


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(60))
    description = db.Column(db.Text)
    duration = db.Column(db.Float)                   # hours
    estimated_cost = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(400))

    def __repr__(self):
        return f"<Activity {self.name}>"