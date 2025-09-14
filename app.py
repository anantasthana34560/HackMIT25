import os
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extractor import extract_travel_info
from app_cool import ai_travel_agent_agno
from housing_listings import housing_id_dict
from cuisine_listings import cuisine_id_dict
from experience_listings import experience_id_dict

# --- Load environment variables ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Flask setup ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecret'
db = SQLAlchemy(app)

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- Database models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    destination = db.Column(db.String(120))
    dates = db.Column(db.String(120))
    style = db.Column(db.String(120))
    cuisine = db.Column(db.String(120))
    activities = db.Column(db.String(120))
    plan = db.Column(db.Text)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(username=username).first():
            return "Username already exists!"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    return render_template("home.html", user=current_user)

# --- New: start flow from freeform prompt + dates + travelers ---
@app.route("/start", methods=["POST"]) 
@login_required
def start():
    # Gather inputs
    freeform_text = request.form.get("freeform_text", "")
    input_dates = request.form.get("dates", "").strip()
    travelers = request.form.get("travelers", "").strip()

    # Extract info from freeform text
    extracted = extract_travel_info(freeform_text or "")

    # Merge dates/travelers overrides
    if input_dates:
        # naive split: support comma or slash separated
        extracted["dates"] = [d.strip() for d in input_dates.replace("/", ",").split(",") if d.strip()]
    if travelers:
        extracted["travelers"] = travelers

    # Build user_preferences and travel_info dicts expected by agent
    user_preferences_dict = {
        "housing_type": extracted.get("housing_type", []) or ["House", "Apartment", "Hotel"],
        "preferred_amenities": extracted.get("desired_amenities", []),
        "safety_level": extracted.get("safety_level") or "High",
        "price_range": extracted.get("price_range", [50, 150]),
        "cuisine_types": [c.capitalize() for c in extracted.get("cuisine_types", [])],
        "experience_types": [e.capitalize() for e in extracted.get("experience_types", [])],
    }

    travel_info_dict = {
        "location": extracted.get("location") or request.form.get("destination") or "Boston, USA",
        "dates": extracted.get("dates", []),
        "desired_amenities": extracted.get("desired_amenities", []),
        "travelers": extracted.get("travelers") or travelers or 1,
        "cuisine_preferences": user_preferences_dict["cuisine_types"],
        "experience_preferences": user_preferences_dict["experience_types"],
    }

    # Run agent
    recs = ai_travel_agent_agno(user_preferences_dict, travel_info_dict)

    # Persist for swipe phase
    session["travel_info_dict"] = travel_info_dict
    session["user_preferences_dict"] = user_preferences_dict
    session["candidates"] = {
        "housing_ids": recs.housing_ids,
        "cuisine_ids": recs.cuisine_ids,
        "experience_ids": recs.experience_ids,
    }
    session["likes"] = {"housing": [], "cuisine": [], "experience": []}
    session["dislikes"] = {"housing": [], "cuisine": [], "experience": []}

    return redirect(url_for("swipe"))


@app.route("/swipe", methods=["GET"])
@login_required
def swipe():
    candidates = session.get("candidates", {"housing_ids": [], "cuisine_ids": [], "experience_ids": []})
    housing_cards = [housing_id_dict[i] for i in candidates.get("housing_ids", []) if i in housing_id_dict]
    cuisine_cards = [cuisine_id_dict[i] for i in candidates.get("cuisine_ids", []) if i in cuisine_id_dict]
    experience_cards = [experience_id_dict[i] for i in candidates.get("experience_ids", []) if i in experience_id_dict]
    return render_template("swipe_interface.html", housing_cards=housing_cards, cuisine_cards=cuisine_cards, experience_cards=experience_cards)


@app.route("/swipe/action", methods=["POST"]) 
@login_required
def swipe_action():
    item_id = request.form.get("id")
    kind = request.form.get("kind")  # housing|cuisine|experience
    action = request.form.get("action")  # like|dislike
    if not item_id or kind not in ("housing", "cuisine", "experience") or action not in ("like", "dislike"):
        return ("bad request", 400)
    likes = session.get("likes", {"housing": [], "cuisine": [], "experience": []})
    dislikes = session.get("dislikes", {"housing": [], "cuisine": [], "experience": []})
    if action == "like":
        if item_id not in likes[kind]:
            likes[kind].append(item_id)
        if item_id in dislikes[kind]:
            dislikes[kind].remove(item_id)
    else:
        if item_id not in dislikes[kind]:
            dislikes[kind].append(item_id)
        if item_id in likes[kind]:
            likes[kind].remove(item_id)
    session["likes"] = likes
    session["dislikes"] = dislikes
    return ("ok", 200)


@app.route("/finalize", methods=["POST"]) 
@login_required
def finalize():
    likes = session.get("likes", {"housing": [], "cuisine": [], "experience": []})
    travel_info_dict = session.get("travel_info_dict", {})

    # Build display cards from likes
    housing_cards = [housing_id_dict[i] for i in likes.get("housing", []) if i in housing_id_dict]
    cuisine_cards = [cuisine_id_dict[i] for i in likes.get("cuisine", []) if i in cuisine_id_dict]
    experience_cards = [experience_id_dict[i] for i in likes.get("experience", []) if i in experience_id_dict]

    # TODO: call second agent to assemble final itinerary from likes
    final_plan = {
        "days": [
            {
                "title": "Day 1",
                "housing": housing_cards[:1],
                "dining": cuisine_cards[:1],
                "experience": experience_cards[:1],
            }
        ],
        "notes": "Prototype itinerary assembled from your likes."
    }

    return render_template("final_results.html", plan=final_plan, housing_cards=housing_cards, cuisine_cards=cuisine_cards, experience_cards=experience_cards, travel_info=travel_info_dict)

@app.route("/plan", methods=["POST"])
@login_required
def plan():
    destination = request.form.get("destination")
    dates = request.form.get("dates")
    style = request.form.get("style")
    cuisine = request.form.get("cuisine")
    activities = request.form.get("activities")

    prompt = f"""
    You are a travel expert. Create a 3-day itinerary for a trip:
    - Destination: {destination}
    - Dates: {dates}
    - Travel style: {style}
    - Cuisine preference: {cuisine}
    - Activities preference: {activities}
    Include: recommended restaurants, excursions/activities, and day-by-day suggestions.
    Return it in a clear text format with bullet points or days separated.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert travel planner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        plan_text = response.choices[0].message.content
        plan_lines = plan_text.split("\n")

        # Save trip
        new_trip = Trip(
            user_id=current_user.id,
            destination=destination,
            dates=dates,
            style=style,
            cuisine=cuisine,
            activities=activities,
            plan=plan_text
        )
        db.session.add(new_trip)
        db.session.commit()

    except Exception as e:
        plan_lines = [f"Error: {e}"]

    return render_template("results.html", plan=plan_lines)

@app.route("/trips")
@login_required
def trips():
    user_trips = Trip.query.filter_by(user_id=current_user.id).all()
    return render_template("trips.html", trips=user_trips)













# import os
# from flask import Flask, render_template, request, redirect, url_for
# from dotenv import load_dotenv
# from openai import OpenAI
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

# # --- Load environment variables ---
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Flask setup ---
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'supersecret'
# db = SQLAlchemy(app)

# # --- Flask-Login setup ---
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # --- Database models ---
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)

# class Trip(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
#     destination = db.Column(db.String(120))
#     dates = db.Column(db.String(120))
#     style = db.Column(db.String(120))
#     plan = db.Column(db.Text)

# # Create DB if not exists
# with app.app_context():
#     db.create_all()

# # --- User loader ---
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # --- Routes ---
# @app.route("/")
# def home():
#     return render_template("home.html", user=current_user)

# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = generate_password_hash(request.form["password"])
#         if User.query.filter_by(username=username).first():
#             return "Username already exists!"
#         new_user = User(username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for("login"))
#     return render_template("signup.html")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for("home"))
#         return "Invalid credentials!"
#     return render_template("login.html")

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("home"))

# @app.route("/plan", methods=["POST"])
# @login_required
# def plan():
#     destination = request.form.get("destination")
#     dates = request.form.get("dates")
#     style = request.form.get("style")
#     cuisine = request.form.get("cuisine")
#     activities = request.form.get("activities")

#     prompt = f"""
#     You are a travel expert. Create a 3-day itinerary for a trip:
#     - Destination: {destination}
#     - Dates: {dates}
#     - Travel style: {style}
#     - Cuisine preference: {cuisine}
#     - Activities preference: {activities}
#     Include: recommended restaurants, excursions/activities, and day-by-day suggestions.
#     Return it in a clear text format with bullet points or days separated.
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert travel planner."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=500
#         )
#         plan_text = response.choices[0].message.content
#         plan_lines = plan_text.split("\n")

#         # Save trip with extra info
#         new_trip = Trip(
#             user_id=current_user.id,
#             destination=destination,
#             dates=dates,
#             style=style,
#             plan=plan_text
#         )
#         db.session.add(new_trip)
#         db.session.commit()

#     except Exception as e:
#         plan_lines = [f"Error: {e}"]

#     return render_template("results.html", plan=plan_lines)

# def plan():
#     destination = request.form.get("destination")
#     dates = request.form.get("dates")
#     style = request.form.get("style")

#     prompt = f"Create a short 3-day itinerary for {destination} ({dates}), style: {style}. Give each day as a separate line."

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert travel planner."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=300
#         )
#         plan_text = response.choices[0].message.content
#         plan_lines = plan_text.split("\n")

#         # Save trip
#         new_trip = Trip(user_id=current_user.id, destination=destination, dates=dates, style=style, plan=plan_text)
#         db.session.add(new_trip)
#         db.session.commit()

#     except Exception as e:
#         plan_lines = [f"Error: {e}"]

#     return render_template("results.html", plan=plan_lines)

@app.route("/trips")
@login_required
def trips():
    user_trips = Trip.query.filter_by(user_id=current_user.id).all()
    return render_template("trips.html", trips=user_trips)

# --- Run app ---
if __name__ == "__main__":
    app.run(debug=True)














# import os
# from flask import Flask, render_template, request, redirect, url_for
# from dotenv import load_dotenv
# from openai import OpenAI
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

# # --- Load env and OpenAI ---
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Flask setup ---
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'supersecret'
# db = SQLAlchemy(app)

# # --- Login manager ---
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # --- Database models ---
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     password = db.Column(db.String(200))

# class Trip(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
#     destination = db.Column(db.String(120))
#     dates = db.Column(db.String(120))
#     style = db.Column(db.String(120))
#     plan = db.Column(db.Text)

# with app.app_context():
#     db.create_all()

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # --- Routes ---

# # Home
# @app.route("/")
# def home():
#     return render_template("home.html", user=current_user)

# # Signup
# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = generate_password_hash(request.form["password"])
#         if User.query.filter_by(username=username).first():
#             return "Username already exists!"
#         new_user = User(username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for("login"))
#     return render_template("signup.html")

# # Login
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for("home"))
#         return "Invalid credentials!"
#     return render_template("login.html")

# # Logout
# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("home"))

# # Plan AI Trip
# @app.route("/plan", methods=["POST"])
# @login_required
# def plan():
#     destination = request.form.get("destination")
#     dates = request.form.get("dates")
#     style = request.form.get("style")

#     prompt = f"Create a short 3-day itinerary for {destination} ({dates}), style: {style}. Give each day as a separate line."

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert travel planner."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=300
#         )
#         plan_text = response.choices[0].message.content
#         plan_lines = plan_text.split("\n")

#         # Save trip to database with user_id
#         new_trip = Trip(user_id=current_user.id, destination=destination, dates=dates, style=style, plan=plan_text)
#         db.session.add(new_trip)
#         db.session.commit()

#     except Exception as e:
#         plan_lines = [f"Error: {e}"]

#     return render_template("results.html", plan=plan_lines)

# # View Saved Trips
# @app.route("/trips")
# @login_required
# def trips():
#     user_trips = Trip.query.filter_by(user_id=current_user.id).all()
#     return render_template("trips.html", trips=user_trips)





# import os
# from flask import Flask, render_template, request, redirect, url_for
# from dotenv import load_dotenv
# from openai import OpenAI
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

# # --- Load env and OpenAI ---
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Flask setup ---
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'supersecret'
# db = SQLAlchemy(app)

# # --- Login manager ---
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # --- Database models ---
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     password = db.Column(db.String(200))

# class Trip(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
#     destination = db.Column(db.String(120))
#     dates = db.Column(db.String(120))
#     style = db.Column(db.String(120))
#     plan = db.Column(db.Text)

# with app.app_context():
#     db.create_all()

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # --- Routes ---

# # Home
# @app.route("/")
# def home():
#     return render_template("home.html", user=current_user)

# # Signup
# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = generate_password_hash(request.form["password"])
#         if User.query.filter_by(username=username).first():
#             return "Username already exists!"
#         new_user = User(username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for("login"))
#     return render_template("signup.html")

# # Login
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for("home"))
#         return "Invalid credentials!"
#     return render_template("login.html")

# # Logout
# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("home"))

# # Plan AI Trip
# @app.route("/plan", methods=["POST"])
# @login_required
# def plan():
#     destination = request.form.get("destination")
#     dates = request.form.get("dates")
#     style = request.form.get("style")

#     prompt = f"Create a short 3-day itinerary for {destination} ({dates}), style: {style}. Give each day as a separate line."

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert travel planner."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=300
#         )
#         plan_text = response.choices[0].message.content
#         plan_lines = plan_text.split("\n")

#         # Save trip to database with user_id
#         new_trip = Trip(user_id=current_user.id, destination=destination, dates=dates, style=style, plan=plan_text)
#         db.session.add(new_trip)
#         db.session.commit()

#     except Exception as e:
#         plan_lines = [f"Error: {e}"]

#     return render_template("results.html", plan=plan_lines)

# # View Saved Trips
# @app.route("/trips")
# @login_required
# def trips():
#     user_trips = Trip.query.filter_by(user_id=current_user.id).all()
#     return render_template("trips.html", trips=user_trips)


#  import os
# from flask import Flask, render_template, request
# from dotenv import load_dotenv
# from openai import OpenAI
# from flask_sqlalchemy import SQLAlchemy

# # --- Load environment variables ---
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Flask app setup ---
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # --- Database model ---
# class Trip(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     destination = db.Column(db.String(120))
#     dates = db.Column(db.String(120))
#     style = db.Column(db.String(120))
#     plan = db.Column(db.Text)

# with app.app_context():
#     db.create_all()

# # --- Routes ---
# @app.route("/")
# def home():
#     return render_template("home.html")

# @app.route("/plan", methods=["POST"])
# def plan():
#     destination = request.form.get("destination")
#     dates = request.form.get("dates")
#     style = request.form.get("style")

#     prompt = f"""
#     You are an expert travel planner. Create a short 3-day itinerary for a trip.
#     Destination: {destination}
#     Dates: {dates}
#     Style: {style}
#     Return the plan as a list of day-by-day suggestions with activities and meals.
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert travel planner."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=300
#         )
#         plan_text = response.choices[0].message.content
#         plan_lines = plan_text.split("\n")

#         # --- Save trip to database ---
#         new_trip = Trip(destination=destination, dates=dates, style=style, plan=plan_text)
#         db.session.add(new_trip)
#         db.session.commit()

#     except Exception as e:
#         plan_lines = [f"Error: {e}"]

#     return render_template("results.html", plan=plan_lines)

# @app.route("/trips")
# def trips():
#     all_trips = Trip.query.all()
#     return render_template("trips.html", trips=all_trips)

# # --- Run app ---
# if __name__ == "__main__":
#     app.run(debug=True)






# import os
# from flask import Flask, render_template, request
# from dotenv import load_dotenv
# from openai import OpenAI

# # --- Load environment variables ---
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Flask app setup ---
# app = Flask(__name__)

# # --- Home page with travel form ---
# @app.route("/")
# def home():
#     return render_template("home.html")

# # --- Plan route: generates AI itinerary ---
# @app.route("/plan", methods=["POST"])
# def plan():
#     destination = request.form.get("destination")
#     dates = request.form.get("dates")
#     style = request.form.get("style")

#     # Build AI prompt
#     prompt = f"""
#     You are an expert travel planner. Create a short 3-day itinerary for a trip.
#     Destination: {destination}
#     Dates: {dates}
#     Style: {style}
#     Return the plan as a list of day-by-day suggestions with activities and meals.
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",  # You can also use gpt-4 or gpt-3.5-turbo
#             messages=[
#                 {"role": "system", "content": "You are an expert travel planner."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=300
#         )

#         # Extract the AI-generated text
#         plan_text = response.choices[0].message.content
#         # Split into a list by lines
#         plan_lines = plan_text.split("\n")

#     except Exception as e:
#         plan_lines = [f"Error: {e}"]

#     # Render results page
#     return render_template("results.html", plan=plan_lines)

# # --- Run app ---
# if __name__ == "__main__":
#     app.run(debug=True)










# # from flask import Flask, render_template, request, redirect, url_for, session
# # from flask_sqlalchemy import SQLAlchemy
# # from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# # from werkzeug.security import generate_password_hash, check_password_hash

# # # --- FLASK SETUP ---
# # app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# # app.config['SECRET_KEY'] = "supersecret"  # Needed for sessions
# # db = SQLAlchemy(app)

# # login_manager = LoginManager()
# # login_manager.init_app(app)
# # login_manager.login_view = "login"

# # # --- DATABASE MODELS ---
# # class User(UserMixin, db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     username = db.Column(db.String(80), unique=True)
# #     password = db.Column(db.String(200))

# # class Trip(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
# #     destination = db.Column(db.String(120))
# #     dates = db.Column(db.String(120))
# #     style = db.Column(db.String(120))
# #     plan = db.Column(db.Text)

# # with app.app_context():
# #     db.create_all()

# # @login_manager.user_loader
# # def load_user(user_id):
# #     return User.query.get(int(user_id))

# # # --- AUTH ROUTES ---
# # @app.route("/signup", methods=["GET", "POST"])
# # def signup():
# #     if request.method == "POST":
# #         username = request.form["username"]
# #         password = generate_password_hash(request.form["password"])
# #         if User.query.filter_by(username=username).first():
# #             return "Username already exists!"
# #         new_user = User(username=username, password=password)
# #         db.session.add(new_user)
# #         db.session.commit()
# #         return redirect(url_for("login"))
# #     return render_template("signup.html")

# # @app.route("/login", methods=["GET", "POST"])
# # def login():
# #     if request.method == "POST":
# #         username = request.form["username"]
# #         password = request.form["password"]
# #         user = User.query.filter_by(username=username).first()
# #         if user and check_password_hash(user.password, password):
# #             login_user(user)
# #             return redirect(url_for("home"))
# #         return "Invalid credentials!"
# #     return render_template("login.html")

# # @app.route("/logout")
# # def logout():
# #     logout_user()
# #     return redirect(url_for("home"))

# # # --- MODIFY EXISTING ROUTES ---
# # @app.route("/")
# # def home():
# #     return render_template("home.html", user=current_user)

# # @app.route("/plan", methods=["POST"])
# # @login_required
# # def plan():
# #     # ... same as before, but add user_id when saving trip
# #     new_trip = Trip(user_id=current_user.id, destination=destination, dates=dates, style=style, plan=plan_text)
# #     db.session.add(new_trip)
# #     db.session.commit()
# #     return render_template("results.html", plan=plan_lines)

# # @app.route("/trips")
# # @login_required
# # def trips():
# #     user_trips = Trip.query.filter_by(user_id=current_user.id).all()
# #     return render_template("trips.html", trips=user_trips)
