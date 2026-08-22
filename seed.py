"""Seed data for GlobeTrotter — Indian travel destinations.

Run with:  python seed.py
Drops every table, recreates them, and repopulates. Safe to re-run.

Scope note: this app covers India only. Cities carry a state, so the picker
reads "Udaipur, Rajasthan, India".
"""

from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models import User, City, Activity, Trip, Stop, TripActivity, Expense

# name, state, lat, lon, cost_index (1 cheap .. 5 luxury), popularity, image
CITIES = [
    ("Jaipur",        "Rajasthan",         26.9124, 75.7873, 1, 88, "photo-1477587458883-47145ed94245"),
    ("Udaipur",       "Rajasthan",         24.5854, 73.7125, 2, 85, "photo-1609766857041-ed402ea8069a"),
    ("Jaisalmer",     "Rajasthan",         26.9157, 70.9083, 1, 74, "photo-1590766940554-153a4d9866d1"),
    ("Jodhpur",       "Rajasthan",         26.2389, 73.0243, 1, 72, "photo-1524229664653-b1b4b2b1b3a1"),
    ("Goa",           "Goa",               15.2993, 74.1240, 2, 91, "photo-1512343879784-a960bf40e7f2"),
    ("Mumbai",        "Maharashtra",       19.0760, 72.8777, 3, 89, "photo-1570168007204-dfb528c6958f"),
    ("Pune",          "Maharashtra",       18.5204, 73.8567, 2, 68, "photo-1567157577867-05ccb1388e66"),
    ("New Delhi",     "Delhi",             28.6139, 77.2090, 2, 90, "photo-1587474260584-136574528ed5"),
    ("Agra",          "Uttar Pradesh",     27.1767, 78.0081, 1, 93, "photo-1564507592333-c60657eea523"),
    ("Varanasi",      "Uttar Pradesh",     25.3176, 82.9739, 1, 84, "photo-1561361058-c24cecae35ca"),
    ("Rishikesh",     "Uttarakhand",       30.0869, 78.2676, 1, 79, "photo-1591018653367-7ba4c4d0b1a8"),
    ("Manali",        "Himachal Pradesh",  32.2432, 77.1892, 2, 82, "photo-1626621341517-bbf3d9990a23"),
    ("Shimla",        "Himachal Pradesh",  31.1048, 77.1734, 2, 76, "photo-1597074866923-dc0589150358"),
    ("Leh",           "Ladakh",            34.1526, 77.5771, 3, 81, "photo-1581793745862-99fde7fa73d2"),
    ("Srinagar",      "Jammu and Kashmir", 34.0837, 74.7973, 2, 80, "photo-1595815771614-ade9d652a65d"),
    ("Amritsar",      "Punjab",            31.6340, 74.8723, 1, 77, "photo-1588083949404-c4f1ed1323b3"),
    ("Kolkata",       "West Bengal",       22.5726, 88.3639, 1, 75, "photo-1558431382-27e303142255"),
    ("Darjeeling",    "West Bengal",       27.0360, 88.2627, 1, 73, "photo-1544634076-a90160ddf44c"),
    ("Bengaluru",     "Karnataka",         12.9716, 77.5946, 3, 71, "photo-1596176530529-78163a4f7af2"),
    ("Hampi",         "Karnataka",         15.3350, 76.4600, 1, 70, "photo-1600100397608-f010d0e1d1e0"),
    ("Mysuru",        "Karnataka",         12.2958, 76.6394, 1, 69, "photo-1600112356915-089abb8fc71a"),
    ("Kochi",         "Kerala",             9.9312, 76.2673, 2, 78, "photo-1590123732197-e4b1a26b8b0f"),
    ("Munnar",        "Kerala",            10.0889, 77.0595, 2, 74, "photo-1591017403286-fd8493524e1e"),
    ("Alleppey",      "Kerala",             9.4981, 76.3388, 2, 76, "photo-1593693411515-c20261bcad6e"),
    ("Chennai",       "Tamil Nadu",        13.0827, 80.2707, 2, 67, "photo-1582510003544-4d00b7f74220"),
    ("Ooty",          "Tamil Nadu",        11.4102, 76.6950, 1, 66, "photo-1580889240912-c39ea4d5ba0d"),
    ("Hyderabad",     "Telangana",         17.3850, 78.4867, 2, 72, "photo-1572445271230-a78b5944a659"),
    ("Shillong",      "Meghalaya",         25.5788, 91.8933, 1, 64, "photo-1605649487212-47bdab064df7"),
    ("Gangtok",       "Sikkim",            27.3389, 88.6065, 2, 68, "photo-1622308644420-b20142dc993c"),
    ("Puri",          "Odisha",            19.8135, 85.8312, 1, 62, "photo-1600100397608-f010d0e1d1e0"),
    ("Ahmedabad",     "Gujarat",           23.0225, 72.5714, 1, 65, "photo-1583266968949-5a4e0b0d1e18"),
    ("Rann of Kutch", "Gujarat",           23.7337, 69.8597, 1, 63, "photo-1609920658906-8223bd289001"),
]

# city, activity, category, duration_hrs, cost (INR)
ACTIVITIES = [
    ("Jaipur", "Amber Fort", "History", 3.0, 600),
    ("Jaipur", "Hawa Mahal", "Sightseeing", 1.0, 200),
    ("Jaipur", "City Palace Jaipur", "History", 2.5, 700),
    ("Jaipur", "Chokhi Dhani Dinner", "Food", 3.0, 1200),
    ("Udaipur", "Lake Pichola Boat Ride", "Leisure", 1.5, 700),
    ("Udaipur", "City Palace Udaipur", "History", 2.5, 400),
    ("Udaipur", "Monsoon Palace Sunset", "Sightseeing", 2.0, 300),
    ("Jaisalmer", "Sam Sand Dunes Safari", "Adventure", 4.0, 1500),
    ("Jaisalmer", "Jaisalmer Fort Walk", "History", 2.5, 250),
    ("Jaisalmer", "Desert Camp Night", "Leisure", 12.0, 2500),
    ("Jodhpur", "Mehrangarh Fort", "History", 3.0, 600),
    ("Jodhpur", "Blue City Walk", "Sightseeing", 2.0, 0),
    ("Goa", "Dudhsagar Falls Trip", "Nature", 6.0, 1800),
    ("Goa", "Old Goa Churches", "History", 3.0, 0),
    ("Goa", "Anjuna Flea Market", "Leisure", 2.5, 0),
    ("Goa", "Scuba at Grande Island", "Adventure", 5.0, 3500),
    ("Mumbai", "Gateway of India", "Sightseeing", 1.0, 0),
    ("Mumbai", "Elephanta Caves", "History", 4.0, 1200),
    ("Mumbai", "Marine Drive Evening", "Leisure", 1.5, 0),
    ("Mumbai", "Mohammed Ali Road Food Walk", "Food", 2.5, 900),
    ("Pune", "Shaniwar Wada", "History", 1.5, 150),
    ("Pune", "Sinhagad Fort Trek", "Adventure", 4.0, 300),
    ("New Delhi", "Red Fort", "History", 2.5, 600),
    ("New Delhi", "Qutub Minar", "History", 1.5, 600),
    ("New Delhi", "Humayun Tomb", "History", 2.0, 600),
    ("New Delhi", "Chandni Chowk Food Crawl", "Food", 3.0, 800),
    ("Agra", "Taj Mahal at Sunrise", "History", 3.0, 1300),
    ("Agra", "Agra Fort", "History", 2.0, 650),
    ("Agra", "Mehtab Bagh Sunset", "Sightseeing", 1.5, 300),
    ("Varanasi", "Ganga Aarti at Dashashwamedh", "Sightseeing", 2.0, 0),
    ("Varanasi", "Sunrise Boat Ride", "Leisure", 2.0, 800),
    ("Varanasi", "Sarnath Excursion", "History", 3.0, 500),
    ("Rishikesh", "White Water Rafting", "Adventure", 4.0, 1500),
    ("Rishikesh", "Beatles Ashram", "Leisure", 2.0, 300),
    ("Rishikesh", "Sunrise Yoga Session", "Leisure", 1.5, 500),
    ("Manali", "Solang Valley Paragliding", "Adventure", 3.0, 3000),
    ("Manali", "Hadimba Temple", "History", 1.0, 0),
    ("Manali", "Old Manali Cafe Hop", "Food", 2.5, 700),
    ("Shimla", "Toy Train to Shimla", "Leisure", 5.0, 1000),
    ("Shimla", "Jakhoo Temple Walk", "Nature", 2.0, 0),
    ("Leh", "Pangong Lake Day Trip", "Nature", 10.0, 4000),
    ("Leh", "Nubra Valley Camel Safari", "Adventure", 6.0, 2500),
    ("Leh", "Thiksey Monastery", "History", 2.0, 100),
    ("Srinagar", "Dal Lake Shikara Ride", "Leisure", 2.0, 800),
    ("Srinagar", "Mughal Gardens", "Nature", 3.0, 200),
    ("Srinagar", "Gulmarg Gondola", "Adventure", 5.0, 2000),
    ("Amritsar", "Golden Temple", "History", 2.5, 0),
    ("Amritsar", "Wagah Border Ceremony", "Sightseeing", 3.0, 0),
    ("Amritsar", "Amritsari Kulcha Trail", "Food", 2.0, 500),
    ("Kolkata", "Victoria Memorial", "History", 2.0, 500),
    ("Kolkata", "Howrah Bridge Walk", "Sightseeing", 1.5, 0),
    ("Kolkata", "Park Street Food Tour", "Food", 3.0, 900),
    ("Darjeeling", "Tiger Hill Sunrise", "Nature", 3.0, 600),
    ("Darjeeling", "Tea Garden Tour", "Nature", 2.5, 500),
    ("Bengaluru", "Lalbagh Botanical Garden", "Nature", 2.0, 100),
    ("Bengaluru", "Bangalore Palace", "History", 2.0, 500),
    ("Hampi", "Virupaksha Temple", "History", 2.0, 100),
    ("Hampi", "Boulder Sunset at Hemakuta", "Sightseeing", 2.0, 0),
    ("Hampi", "Coracle Ride on Tungabhadra", "Leisure", 1.0, 400),
    ("Mysuru", "Mysore Palace", "History", 2.5, 400),
    ("Mysuru", "Chamundi Hill", "Nature", 2.5, 200),
    ("Kochi", "Fort Kochi Heritage Walk", "History", 2.5, 400),
    ("Kochi", "Kathakali Performance", "Leisure", 2.0, 600),
    ("Kochi", "Chinese Fishing Nets", "Sightseeing", 1.0, 0),
    ("Munnar", "Tea Plantation Trek", "Nature", 4.0, 800),
    ("Munnar", "Eravikulam National Park", "Nature", 3.0, 600),
    ("Alleppey", "Backwater Houseboat Stay", "Leisure", 20.0, 6000),
    ("Alleppey", "Canoe Village Tour", "Nature", 3.0, 1200),
    ("Chennai", "Marina Beach", "Leisure", 1.5, 0),
    ("Chennai", "Kapaleeshwarar Temple", "History", 1.5, 0),
    ("Chennai", "Mahabalipuram Day Trip", "History", 6.0, 1500),
    ("Ooty", "Nilgiri Mountain Railway", "Leisure", 4.0, 800),
    ("Ooty", "Botanical Gardens Ooty", "Nature", 2.0, 200),
    ("Hyderabad", "Charminar", "History", 1.5, 100),
    ("Hyderabad", "Golconda Fort", "History", 3.0, 400),
    ("Hyderabad", "Biryani Tasting Trail", "Food", 2.5, 800),
    ("Shillong", "Living Root Bridges Trek", "Adventure", 6.0, 1200),
    ("Shillong", "Elephant Falls", "Nature", 1.5, 200),
    ("Gangtok", "Tsomgo Lake", "Nature", 5.0, 2000),
    ("Gangtok", "Rumtek Monastery", "History", 2.5, 200),
    ("Puri", "Jagannath Temple", "History", 2.0, 0),
    ("Puri", "Konark Sun Temple", "History", 3.0, 600),
    ("Ahmedabad", "Sabarmati Ashram", "History", 2.0, 0),
    ("Ahmedabad", "Adalaj Stepwell", "History", 1.5, 300),
    ("Ahmedabad", "Manek Chowk Night Food", "Food", 2.0, 500),
    ("Rann of Kutch", "White Desert at Full Moon", "Sightseeing", 4.0, 1500),
    ("Rann of Kutch", "Kutchi Handicraft Villages", "Leisure", 3.0, 600),
]

UNSPLASH = "https://images.unsplash.com/{}?w=800&q=80"

# The demo trip: the classic Golden Triangle.
# city, arrive, leave, [activities], accommodation, food, transport
DEMO_PLAN = [
    ("New Delhi", date(2026, 9, 10), date(2026, 9, 13),
     ["Red Fort", "Qutub Minar", "Chandni Chowk Food Crawl"], 9000, 3500, 4000),
    ("Agra", date(2026, 9, 13), date(2026, 9, 16),
     ["Taj Mahal at Sunrise", "Agra Fort", "Mehtab Bagh Sunset"], 7500, 3000, 2500),
    ("Jaipur", date(2026, 9, 16), date(2026, 9, 20),
     ["Amber Fort", "Hawa Mahal", "City Palace Jaipur", "Chokhi Dhani Dinner"],
     11000, 4500, 3000),
]


def seed():
    db.drop_all()
    db.create_all()

    city_map = {}
    for name, state, lat, lon, ci, pop, img in CITIES:
        c = City(name=name, state=state, country="India", lat=lat, lon=lon,
                 cost_index=ci, popularity=pop,
                 image_url=UNSPLASH.format(img))
        db.session.add(c)
        city_map[name] = c
    # flush assigns primary keys without committing, so the foreign keys below
    # resolve. Without it every city_id comes out None.
    db.session.flush()

    act_map = {}
    for city_name, name, cat, dur, cost in ACTIVITIES:
        a = Activity(city_id=city_map[city_name].id, name=name,
                     category=cat, duration=dur, estimated_cost=cost,
                     description=f"{cat} experience in {city_name}.")
        db.session.add(a)
        act_map[name] = a
    db.session.flush()

    demo = User(first_name="Demo", last_name="User", username="demo",
                email="demo@demo.com", phone="9999999999",
                city="Ahmedabad", country="India",
                password_hash=generate_password_hash("demo1234"))
    db.session.add(demo)
    db.session.flush()

    trip = Trip(user_id=demo.id, name="Golden Triangle 2026",
                description="Delhi, Agra and Jaipur in ten days — forts, "
                            "marble and far too much street food.",
                start_date=date(2026, 9, 10), end_date=date(2026, 9, 20),
                is_public=True, share_token="demo1234",
                cover_image=city_map["Agra"].image_url)
    db.session.add(trip)
    db.session.flush()

    for i, (city_name, sd, ed, acts, stay, food, transport) in enumerate(DEMO_PLAN):
        stop = Stop(trip_id=trip.id, city_id=city_map[city_name].id,
                    start_date=sd, end_date=ed, position=i)
        db.session.add(stop)
        db.session.flush()

        for j, act_name in enumerate(acts):
            a = act_map[act_name]
            db.session.add(TripActivity(
                stop_id=stop.id, activity_id=a.id, name=a.name,
                cost=a.estimated_cost, position=j,
                # spread activities over consecutive days so the itinerary
                # view shows a real Day 1 / Day 2 / Day 3 breakdown
                date=min(sd + timedelta(days=j), ed)))

        for category, amount, label in (
            ("Accommodation", stay, f"Hotel in {city_name}"),
            ("Food", food, f"Meals in {city_name}"),
            ("Transport", transport, f"Travel to {city_name}"),
        ):
            db.session.add(Expense(trip_id=trip.id, stop_id=stop.id,
                                   category=category, amount=amount,
                                   description=label))

    db.session.commit()

    states = len({s for _, s, *_ in CITIES})
    print(f"seeded: {len(CITIES)} Indian cities across {states} states, "
          f"{len(ACTIVITIES)} activities, "
          f"demo trip id={trip.id} (login: demo / demo1234)")


if __name__ == "__main__":
    with app.app_context():
        seed()
