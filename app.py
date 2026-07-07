import os

from flask import Flask, render_template, request, redirect, url_for, session

from auth.login import login_user
from auth.signup import register_user
from utils.security_log import log_event

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-change-me-before-production")


@app.context_processor
def inject_native():
    return {"native_app": os.environ.get("CYBERVAULT_NATIVE") == "1"}


def client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)


@app.route("/")
def home():
    if session.get("username"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username"):
        return redirect(url_for("dashboard"))

    error = None
    email = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = login_user(email, password, ip=client_ip())

        if user:
            session["username"] = user["username"]
            session["role"] = user.get("role", "user")
            return redirect(url_for("dashboard"))

        error = "Invalid email or password."

    return render_template("login.html", error=error, email=email)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("username"):
        return redirect(url_for("dashboard"))

    error = None
    email = ""
    username = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = register_user(username, email, password, ip=client_ip())
            session["username"] = user["username"]
            session["role"] = user.get("role", "user")
            return redirect(url_for("dashboard"))
        except ValueError as exc:
            code = str(exc)
            if code == "username_taken":
                error = "That username is already taken."
            elif code == "email_taken":
                error = "An account with that email already exists."
            elif code == "invalid_username":
                error = "Username must be 3–20 characters (letters, numbers, _)."
            elif code == "weak_password":
                error = "Password must be at least 8 characters."
            else:
                error = "Could not create account. Please try again."

    return render_template("signup.html", error=error, email=email, username=username)


@app.route("/dashboard")
def dashboard():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=username)


@app.route("/logout")
def logout():
    username = session.get("username")
    log_event("logout", username=username, ip=client_ip())
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
