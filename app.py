from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

from dotenv import load_dotenv

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)


# -------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------

load_dotenv()


# -------------------------
# CHECK ENVIRONMENT VARIABLES
# -------------------------

database_url = os.getenv("DATABASE_URL")

jwt_secret_key = os.getenv("JWT_SECRET_KEY")


if not database_url:

    raise RuntimeError(
        "DATABASE_URL is not set."
    )


if not jwt_secret_key:

    raise RuntimeError(
        "JWT_SECRET_KEY is not set."
    )


# -------------------------
# FLASK APP
# -------------------------

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)


# -------------------------
# DATABASE CONFIGURATION
# -------------------------

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# -------------------------
# JWT CONFIGURATION
# -------------------------

app.config["JWT_SECRET_KEY"] = jwt_secret_key

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    minutes=1
)

app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
    days=7
)


jwt = JWTManager(app)


# -------------------------
# JWT ERROR HANDLERS
# -------------------------

@jwt.unauthorized_loader
def missing_token(error):

    return jsonify({
        "message": "Access token is missing."
    }), 401


@jwt.invalid_token_loader
def invalid_token(error):

    return jsonify({
        "message": "Invalid access token."
    }), 422


@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):

    if jwt_payload.get("type") == "refresh":

        return jsonify({
            "message": "Refresh token has expired.",
            "code": "refresh_token_expired"
        }), 401

    return jsonify({
        "message": "Access token has expired.",
        "code": "access_token_expired"
    }), 401


# -------------------------
# DATABASE
# -------------------------

db = SQLAlchemy(app)


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


# -------------------------
# HOME PAGE
# -------------------------

@app.route("/", methods=["GET"])
def home():

    return render_template("home.html")


# -------------------------
# LOGIN PAGE + API
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")


    data = request.get_json()


    if not data:

        return jsonify({
            "message": "No data was provided."
        }), 400


    email = data.get("email")

    password = data.get("password")


    if not email or not password:

        return jsonify({
            "message": "Email and password are required."
        }), 400


    user = User.query.filter_by(
        email=email
    ).first()


    if not user:

        return jsonify({
            "message": "Invalid email or password."
        }), 401


    if not check_password_hash(
        user.password_hash,
        password
    ):

        return jsonify({
            "message": "Invalid email or password."
        }), 401


    access_token = create_access_token(
        identity=str(user.id)
    )


    refresh_token = create_refresh_token(
        identity=str(user.id)
    )


    return jsonify({

        "message": "Login successful!",

        "access_token": access_token,

        "refresh_token": refresh_token

    }), 200


# -------------------------
# REGISTER PAGE + API
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template("register.html")


    data = request.get_json()


    if not data:

        return jsonify({
            "message": "No data was provided."
        }), 400


    name = data.get("name")

    email = data.get("email")

    password = data.get("password")


    if not name or not email or not password:

        return jsonify({
            "message": "Name, email and password are required."
        }), 400


    if len(password) < 8:

        return jsonify({
            "message": "Password must be at least 8 characters."
        }), 400


    existing_user = User.query.filter_by(
        email=email
    ).first()


    if existing_user:

        return jsonify({
            "message": "Email already registered."
        }), 409


    password_hash = generate_password_hash(
        password
    )


    new_user = User(
        name=name,
        email=email,
        password_hash=password_hash
    )


    db.session.add(new_user)

    db.session.commit()


    return jsonify({
        "message": "User registered successfully!"
    }), 201


# -------------------------
# DASHBOARD PAGE
# -------------------------

@app.route("/dashboard-page", methods=["GET"])
def dashboard_page():

    return render_template("dashboard.html")


# -------------------------
# PROTECTED DASHBOARD API
# -------------------------

@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():

    user_id = get_jwt_identity()


    return jsonify({

        "message": "Welcome to your dashboard!",

        "user_id": user_id

    }), 200


# -------------------------
# REFRESH ACCESS TOKEN
# -------------------------

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()


    new_access_token = create_access_token(
        identity=user_id
    )


    return jsonify({

        "access_token": new_access_token

    }), 200


# -------------------------
# CREATE DATABASE TABLE
# -------------------------

with app.app_context():

    db.create_all()


# -------------------------
# RUN APPLICATION
# -------------------------

if __name__ == "__main__":

    app.run(debug=False)