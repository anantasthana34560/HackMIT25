import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# --- Load env and OpenAI ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Flask setup ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecret'
db = SQLAlchemy(app)

# --- Login manager ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- Database models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    destination = db.Column(db.String(120))
    dates = db.Column(db.String(120))
    style = db.Column(db.String(120))
    plan = db.Column(db.Text)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

# Home
@app.route("/")
def home():
    return render_template("home.html", user=current_user)

# Signup
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

# Login
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

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# Plan AI Trip
@app.route("/plan", methods=["POST"])
@login_required
def plan():
    destination = request.form.get("destination")
    dates = request.form.get("dates")
    style = request.form.get("style")

    prompt = f"Create a short 3-day itinerary for {destination} ({dates}), style: {style}. Give each day as a separate line."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert travel planner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        plan_text = response.choices[0].message.content
        plan_lines = plan_text.split("\n")

        # Save trip to database with user_id
        new_trip = Trip(user_id=current_user.id, destination=destination, dates=dates, style=style, plan=plan_text)
        db.session.add(new_trip)
        db.session.commit()

    except Exception as e:
        plan_lines = [f"Error: {e}"]

    return render_template("results.html", plan=plan_lines)

# View Saved Trips
@app.route("/trips")
@login_required
def trips():
    user_trips = Trip.query.filter_by(user_id=current_user.id).all()
    return render_template("trips.html", trips=user_trips)


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
