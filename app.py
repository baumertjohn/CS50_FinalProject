import math
import requests
import os

# from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

# Constants
BREWERY_SEARCH = "https://api.openbrewerydb.org/v1/breweries/search"

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///user_rating.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user_rating.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Database table setup
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)


class Brewery(db.Model):
    __tablename__ = "breweries"
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)


class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True)
    brewery_id = db.Column(db.Integer, db.ForeignKey("breweries.id"), nullable=False)
    rating = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating_date = db.Column(db.Date, nullable=False)

    brewery = db.relationship("Brewery", backref=db.backref("ratings", lazy=True))
    user = db.relationship("User", backref=db.backref("ratings", lazy=True))


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Find current breweries and ratings
    user_id = session["user_id"]
    breweries_with_ratings = (
        db.session.query(
            Brewery.id.label("brewery_id"),
            Brewery.name.label("brewery_name"),
            Brewery.city,
            Brewery.state,
            Brewery.rating,
            Brewery.rating_date,
        )
        .join(Rating, Brewery.id == Rating.brewery_id)
        .join(User, Rating.user_id == User.id)
        .filter(User.id == user_id)
        .order_by(Rating.rating_date.desc())
        .all()
    )

    if request.method == "POST":
        session["breweries"] = []
        brewery_search = request.form.get("brewery_search")
        brewery_search = brewery_search.replace(" ", "_").lower()
        response = requests.get(BREWERY_SEARCH, params={"query": brewery_search})
        session["breweries"] = response.json()
        return render_template("search_results.html", breweries=session["breweries"])
    return render_template("index.html", breweries=breweries_with_ratings)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()  # Forget any user_id
    if request.method == "POST":
        # Query database for username
        username = request.form.get("username")
        user = User.query.filter_by(username=username).first()
        # Ensure username exists and password is correct
        if user is None or not check_password_hash(
            user.password_hash, request.form.get("password")
        ):
            return render_template("login.html", error=True)
        session["user_id"] = user.id  # Remember which user has logged in
        session["user_name"] = user.username
        session["breweries"] = []
        return redirect("/")  # Redirect user to home page
    return render_template("login.html", error=False)


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/rating/<int:brewery_id>", methods=["GET", "POST"])
@login_required
def rating(brewery_id):
    session["brewery"] = session["breweries"][brewery_id]
    RATING = ["Poor", "Mediocre", "Average", "Good", "Great"]
    if request.method == "POST":
        beer_quality = request.form.get("beer_quality")
        atmosphere = request.form.get("atmosphere")
        location = request.form.get("location")
        rating_date = request.form.get("rating_date")
        user_rating = math.ceil(
            (
                round(int(beer_quality) / 25)
                + round(int(atmosphere) / 25)
                + round(int(location) / 25)
            )
            / 3
        )  # TODO: Or should this be "floor"?
        # print(beer_quality, atmosphere, location, RATING[user_rating], rating_date)
        return render_template(
            "rating_result.html",
            brewery=session["brewery"],
            rating=RATING[user_rating],
            rating_date=rating_date,
        )
    return render_template(
        "rating.html", brewery=session["brewery"], brewery_id=brewery_id
    )


@app.route("/rating_result", methods=["GET", "POST"])
@login_required
def rating_result():
    if request.method == "POST":
        rating = request.form.get("rating")
        rating_date = request.form.get("rating_date")
        # print(session["brewery"]["name"], rating)
        # Time to add all this to the database...
        # Check if brewery is in database and add brewery
        b = session["brewery"]  # For brevity
        check = db.execute("SELECT * FROM Brewery where api_id = ?", b["id"])
        if len(check) == 0:
            db.execute(
                "INSERT INTO Brewery (api_id, name, city, state) VALUES (?, ?, ?, ?)",
                b["id"],
                b["name"],
                b["city"],
                b["state"],
            )
        # Get new or existing id of brewery
        brewery_db_id = db.execute("SELECT * FROM Brewery where api_id = ?", b["id"])
        # Update Rating table
        db.execute(
            "INSERT INTO Rating (brewery_id, rating, user_id, rating_date) VALUES (?, ?, ?, ?)",
            brewery_db_id[0]["id"],
            rating,
            session["user_id"],
            rating_date,
        )
        return redirect("/")
    return render_template("rating_result.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # check if user in database and add user to database
        user = User.query.filter_by(username=username).first()
        if user is None:
            # Hash the password
            password_hash = generate_password_hash(password)
            # Create a new user and add to the database
            new_user = User(username=username, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            # find user id and login
            user = User.query.filter_by(username=username).first()
            session["user_id"] = user.id
            return redirect("/")
        else:
            return render_template("register.html", error=True)
    return render_template("register.html", error=False)


@app.route("/search_results", methods=["GET", "POST"])
@login_required
def search_results():
    if request.method == "POST":
        return render_template("search_results.html")
    return redirect("/")


if __name__ == "__main__":
    # Check for database and create if needed
    if not os.path.exists("user_rating.db"):
        with app.app_context():
            db.create_all()
    app.run(host="0.0.0.0", port="5000", debug=True)
