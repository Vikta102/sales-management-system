import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from extensions import db
from models import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _get_field(name: str) -> str:
    return (request.form.get(name) or "").strip()


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    identifier = _get_field("identifier")
    password = request.form.get("password") or ""

    if not identifier or not password:
        flash("Please enter your username/email and password.", "warning")
        return redirect(url_for("auth.login"))

    user = (
        User.query.filter(db.func.lower(User.username) == identifier.lower()).first()
        or User.query.filter(db.func.lower(User.email) == identifier.lower()).first()
    )
    if not user or not user.check_password(password):
        flash("Invalid credentials.", "danger")
        return redirect(url_for("auth.login"))

    login_user(user)
    flash("Welcome back!", "success")
    return redirect(url_for("dashboard.index"))


@auth_bp.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    username = _get_field("username")
    email = _get_field("email")
    password = request.form.get("password") or ""
    password2 = request.form.get("password2") or ""

    if not username or not email or not password:
        flash("All fields are required.", "warning")
        return redirect(url_for("auth.register"))
    if password != password2:
        flash("Passwords do not match.", "warning")
        return redirect(url_for("auth.register"))
    if len(password) < 8:
        flash("Password must be at least 8 characters.", "warning")
        return redirect(url_for("auth.register"))

    existing = User.query.filter(
        (db.func.lower(User.username) == username.lower()) | (db.func.lower(User.email) == email.lower())
    ).first()
    if existing:
        flash("Username or email already in use.", "danger")
        return redirect(url_for("auth.register"))

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    logger.info("New user registered: %s", username)

    login_user(user)
    flash("Account created.", "success")
    return redirect(url_for("dashboard.index"))


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
