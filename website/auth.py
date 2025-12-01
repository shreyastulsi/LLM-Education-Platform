from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .supabase_client import get_client

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            res = get_client().auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                session["user_id"] = res.user.id
                session["user_email"] = email
                flash("Logged in", "success")
                return redirect(url_for("home.index"))
        except Exception as exc:
            flash("Login failed. Check credentials.", "error")
            print("Login error:", exc)
    return render_template("auth_login.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            res = get_client().auth.sign_up({"email": email, "password": password})
            if res.user:
                session["user_id"] = res.user.id
                session["user_email"] = email
                flash("Account created and signed in.", "success")
                return redirect(url_for("home.index"))
        except Exception as exc:
            flash("Signup failed. Try a different email/password.", "error")
            print("Signup error:", exc)
    return render_template("auth_signup.html")


@auth.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("home.index"))
