from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models import User, City, Activity, Trip, Stop, TripActivity, Expense

# name, country, lat, lon, cost_index, popularity, image
CITIES = [
    ("Paris", "France", 48.8566, 2.3522, 4, 96, "photo-1502602898657-3e91760cbb34"),
    ("Amsterdam", "Netherlands", 52.3676, 4.9041, 4, 86, "photo-1534351590666-13e3e96b5017"),
    ("Berlin", "Germany", 52.5200, 13.4050, 3, 84, "photo-1560969184-10fe8719e047"),
    ("Rome", "Italy", 41.9028, 12.4964, 3, 92, "photo-1552832230-c0197dd311b5"),
    ("Barcelona", "Spain", 41.3851, 2.1734, 3, 89, "photo-1583422409516-2895a77efded"),
    ("Prague", "Czechia", 50.0755, 14.4378, 2, 80, "photo-1541849546-216549ae216d"),
    ("Lisbon", "Portugal", 38.7223, -9.1393, 2, 78, "photo-1585208798174-6cedd86e019a"),
    ("Vienna", "Austria", 48.2082, 16.3738, 4, 74, "photo-1516550893923-42d28e5677af"),
    ("Istanbul", "Turkey", 41.0082, 28.9784, 2, 85, "photo-1541432901042-2d8bd64b4a9b"),
    ("Tokyo", "Japan", 35.6762, 139.6503, 4, 95, "photo-1540959733332-eab4deabeeaf"),
    ("Kyoto", "Japan", 35.0116, 135.7681, 3, 82, "photo-1493976040374-85c8e12f0c0e"),
    ("Bangkok", "Thailand", 13.7563, 100.5018, 1, 88, "photo-1508009603885-50cf7c579365"),
    ("Bali", "Indonesia", -8.4095, 115.1889, 1, 90, "photo-1537996194471-e657df975ab4"),
    ("Dubai", "UAE", 25.2048, 55.2708, 5, 87, "photo-1512453979798-5ea266f8880c"),
    ("Singapore", "Singapore", 1.3521, 103.8198, 4, 83, "photo-1525625293386-3f8f99389edd"),
    ("New York", "USA", 40.7128, -74.0060, 5, 94, "photo-1496442226666-8d4d0e62e6e9"),
    ("London", "UK", 51.5074, -0.1278, 5, 93, "photo-1513635269975-59663e0ac1ad"),
    ("Reykjavik", "Iceland", 64.1466, -21.9426, 5, 70, "photo-1504541989296-cc7c0e2c4b1c"),
    ("Cairo", "Egypt", 30.0444, 31.2357, 1, 76, "photo-1539650116574-75c0c6d73f6e"),
    ("Cape Town", "South Africa", -33.9249, 18.4241, 2, 79, "photo-1580060839134-75a5edca2e99"),
    ("Sydney", "Australia", -33.8688, 151.2093, 4, 81, "photo-1506973035872-a4ec16b8e8d9"),
    ("Marrakech", "Morocco", 31.6295, -7.9811, 2, 73, "photo-1597212618440-806262de4f6b"),
    ("Zurich", "Switzerland", 47.3769, 8.5417, 5, 68, "photo-1515488764276-beab7607c1e6"),
]

# city, activity, category, duration_hrs, cost (INR)
ACTIVITIES = [
    ("Paris", "Eiffel Tower Summit", "Sightseeing", 2.5, 2800),
    ("Paris", "Louvre Museum", "History", 3.5, 2200),
    ("Paris", "Seine River Cruise", "Leisure", 1.5, 1600),
    ("Paris", "Montmartre Food Walk", "Food", 3.0, 3500),
    ("Paris", "Versailles Day Trip", "History", 6.0, 4200),
    ("Amsterdam", "Van Gogh Museum", "History", 2.5, 2000),
    ("Amsterdam", "Canal Cruise", "Leisure", 1.5, 1800),
    ("Amsterdam", "Anne Frank House", "History", 2.0, 1500),
    ("Amsterdam", "Jordaan Bike Tour", "Adventure", 3.0, 2600),
    ("Berlin", "Brandenburg Gate", "Sightseeing", 1.0, 0),
    ("Berlin", "Berlin Wall Memorial", "History", 2.0, 0),
    ("Berlin", "Museum Island Pass", "History", 4.0, 1900),
    ("Berlin", "Street Food Market", "Food", 2.0, 1200),
    ("Rome", "Colosseum & Forum", "History", 3.5, 2400),
    ("Rome", "Vatican Museums", "History", 4.0, 2900),
    ("Rome", "Trastevere Food Tour", "Food", 3.0, 3800),
    ("Rome", "Pantheon Walk", "Sightseeing", 1.0, 0),
    ("Barcelona", "Sagrada Familia", "Sightseeing", 2.0, 2600),
    ("Barcelona", "Park Guell", "Nature", 2.0, 1200),
    ("Barcelona", "Tapas Crawl", "Food", 3.0, 3200),
    ("Barcelona", "Barceloneta Beach Day", "Leisure", 4.0, 0),
    ("Prague", "Prague Castle", "History", 3.0, 1100),
    ("Prague", "Charles Bridge Sunrise", "Sightseeing", 1.0, 0),
    ("Prague", "Beer Tasting Tour", "Food", 2.5, 1900),
    ("Lisbon", "Belem Tower", "History", 1.5, 900),
    ("Lisbon", "Tram 28 Ride", "Sightseeing", 1.0, 300),
    ("Lisbon", "Sintra Day Trip", "Nature", 6.0, 2800),
    ("Lisbon", "Fado Night", "Leisure", 2.5, 2100),
    ("Vienna", "Schonbrunn Palace", "History", 3.0, 2200),
    ("Vienna", "Opera House Tour", "Leisure", 1.5, 1400),
    ("Vienna", "Cafe Culture Walk", "Food", 2.0, 1600),
    ("Istanbul", "Hagia Sophia", "History", 2.0, 1300),
    ("Istanbul", "Grand Bazaar", "Leisure", 2.5, 0),
    ("Istanbul", "Bosphorus Cruise", "Leisure", 2.0, 1500),
    ("Istanbul", "Turkish Breakfast Tour", "Food", 2.0, 1700),
    ("Tokyo", "Shibuya Crossing & Harajuku", "Sightseeing", 3.0, 0),
    ("Tokyo", "TeamLab Planets", "Leisure", 2.0, 2400),
    ("Tokyo", "Tsukiji Outer Market", "Food", 2.5, 2800),
    ("Tokyo", "Senso-ji Temple", "History", 1.5, 0),
    ("Tokyo", "Robot Restaurant Show", "Leisure", 2.0, 4500),
    ("Kyoto", "Fushimi Inari Shrine", "History", 3.0, 0),
    ("Kyoto", "Arashiyama Bamboo Grove", "Nature", 2.0, 0),
    ("Kyoto", "Tea Ceremony", "Food", 1.5, 3000),
    ("Kyoto", "Gion Evening Walk", "Sightseeing", 2.0, 0),
    ("Bangkok", "Grand Palace", "History", 3.0, 1400),
    ("Bangkok", "Floating Market", "Food", 4.0, 1800),
    ("Bangkok", "Thai Cooking Class", "Food", 3.5, 2200),
    ("Bangkok", "Chatuchak Market", "Leisure", 3.0, 0),
    ("Bali", "Ubud Rice Terraces", "Nature", 3.0, 700),
    ("Bali", "Uluwatu Temple Sunset", "Sightseeing", 2.5, 900),
    ("Bali", "Surf Lesson Canggu", "Adventure", 2.0, 2000),
    ("Bali", "Mount Batur Sunrise Trek", "Adventure", 6.0, 3200),
    ("Dubai", "Burj Khalifa Deck", "Sightseeing", 2.0, 4000),
    ("Dubai", "Desert Safari", "Adventure", 6.0, 5500),
    ("Dubai", "Dubai Mall & Fountain", "Leisure", 3.0, 0),
    ("Singapore", "Gardens by the Bay", "Nature", 3.0, 2100),
    ("Singapore", "Marina Bay Sands SkyPark", "Sightseeing", 1.5, 1900),
    ("Singapore", "Hawker Centre Crawl", "Food", 2.0, 1000),
    ("Singapore", "Sentosa Island Day", "Leisure", 5.0, 3000),
    ("New York", "Statue of Liberty Ferry", "Sightseeing", 4.0, 2600),
    ("New York", "Central Park Walk", "Nature", 2.5, 0),
    ("New York", "MoMA", "History", 3.0, 2300),
    ("New York", "Broadway Show", "Leisure", 3.0, 8000),
    ("New York", "Brooklyn Pizza Tour", "Food", 3.0, 3600),
    ("London", "Tower of London", "History", 3.0, 3100),
    ("London", "British Museum", "History", 3.0, 0),
    ("London", "London Eye", "Sightseeing", 1.0, 3300),
    ("London", "Borough Market", "Food", 2.0, 1500),
    ("London", "West End Theatre", "Leisure", 3.0, 6000),
    ("Reykjavik", "Blue Lagoon", "Leisure", 4.0, 8500),
    ("Reykjavik", "Northern Lights Tour", "Nature", 4.0, 6000),
    ("Reykjavik", "Golden Circle Drive", "Nature", 8.0, 7000),
    ("Cairo", "Pyramids of Giza", "History", 4.0, 1600),
    ("Cairo", "Egyptian Museum", "History", 3.0, 1100),
    ("Cairo", "Nile Dinner Cruise", "Food", 3.0, 2400),
    ("Cape Town", "Table Mountain Cable Car", "Nature", 3.0, 2200),
    ("Cape Town", "Cape Peninsula Drive", "Nature", 7.0, 3800),
    ("Cape Town", "Robben Island Tour", "History", 4.0, 2500),
    ("Cape Town", "Winelands Tasting", "Food", 5.0, 3400),
    ("Sydney", "Opera House Tour", "Sightseeing", 1.5, 2900),
    ("Sydney", "Bondi to Coogee Walk", "Nature", 3.0, 0),
    ("Sydney", "Harbour Bridge Climb", "Adventure", 3.5, 12000),
    ("Sydney", "Blue Mountains Day Trip", "Nature", 8.0, 5200),
    ("Marrakech", "Jemaa el-Fnaa", "Sightseeing", 2.0, 0),
    ("Marrakech", "Majorelle Garden", "Nature", 1.5, 1000),
    ("Marrakech", "Atlas Mountains Day Trip", "Adventure", 8.0, 3600),
    ("Marrakech", "Souk Shopping Walk", "Leisure", 2.5, 0),
    ("Zurich", "Lake Zurich Cruise", "Leisure", 2.0, 2400),
    ("Zurich", "Old Town Walk", "Sightseeing", 2.0, 0),
    ("Zurich", "Swiss Chocolate Tour", "Food", 2.5, 4200),
    ("Zurich", "Uetliberg Hike", "Nature", 3.5, 0),
]

# ---------------------------------------------------------------------------
# India, by state. Same shape as CITIES but carrying a state, so the city
# picker can read "Udaipur, Rajasthan, India".
# name, state, lat, lon, cost_index, popularity, image
# ---------------------------------------------------------------------------
INDIA_CITIES = [
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
INDIA_ACTIVITIES = [
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


def seed():
    db.drop_all()
    db.create_all()

    city_map = {}
    for name, country, lat, lon, ci, pop, img in CITIES:
        c = City(name=name, country=country, lat=lat, lon=lon,
                 cost_index=ci, popularity=pop,
                 image_url=UNSPLASH.format(img))
        db.session.add(c)
        city_map[name] = c

    for name, state, lat, lon, ci, pop, img in INDIA_CITIES:
        c = City(name=name, state=state, country="India", lat=lat, lon=lon,
                 cost_index=ci, popularity=pop,
                 image_url=UNSPLASH.format(img))
        db.session.add(c)
        city_map[name] = c
    db.session.flush()

    act_map = {}
    for city_name, name, cat, dur, cost in ACTIVITIES + INDIA_ACTIVITIES:
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

    trip = Trip(user_id=demo.id, name="Europe 2026",
                description="Three cities, ten days, one very tired camera.",
                start_date=date(2026, 9, 10), end_date=date(2026, 9, 20),
                is_public=True, share_token="demo1234",
                cover_image=city_map["Paris"].image_url)
    db.session.add(trip)
    db.session.flush()

    plan = [
        ("Paris", date(2026, 9, 10), date(2026, 9, 14),
         ["Eiffel Tower Summit", "Louvre Museum", "Seine River Cruise"], 14000),
        ("Amsterdam", date(2026, 9, 14), date(2026, 9, 17),
         ["Van Gogh Museum", "Canal Cruise", "Anne Frank House"], 11000),
        ("Berlin", date(2026, 9, 17), date(2026, 9, 20),
         ["Brandenburg Gate", "Museum Island Pass", "Street Food Market"], 9000),
    ]

    for i, (city_name, sd, ed, acts, stay) in enumerate(plan):
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

        db.session.add(Expense(trip_id=trip.id, stop_id=stop.id,
                               category="Accommodation", amount=stay,
                               description=f"Hotel in {city_name}"))
        db.session.add(Expense(trip_id=trip.id, stop_id=stop.id,
                               category="Food", amount=5000,
                               description=f"Meals in {city_name}"))
        db.session.add(Expense(trip_id=trip.id, stop_id=stop.id,
                               category="Transport", amount=4000,
                               description=f"Travel to {city_name}"))

    db.session.commit()
    states = len({s for _, s, *_ in INDIA_CITIES})
    print(f"seeded: {len(CITIES) + len(INDIA_CITIES)} cities "
          f"({len(INDIA_CITIES)} in India across {states} states), "
          f"{len(ACTIVITIES) + len(INDIA_ACTIVITIES)} activities, "
          f"demo trip id={trip.id} (login: demo / demo1234)")


if __name__ == "__main__":
    with app.app_context():
        seed()