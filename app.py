import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

from auth.login import login_user
from auth.signup import register_user
from config import FLASK_DEBUG, SECRET_KEY, SESSION_COOKIE_SECURE
from utils.access import client_ip, login_required, role_required
from utils.errors import message_for
from utils.rate_limit import check_rate_limit
from utils.security_log import log_event
from utils.session import start_session

load_dotenv()

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=SESSION_COOKIE_SECURE,
)


def _logged_in():
    return bool(session.get("username"))


@app.route("/")
def home():
    if _logged_in():
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if _logged_in():
        return redirect(url_for("dashboard"))

    error = None
    username = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        allowed, rate_error = check_rate_limit(client_ip(), "login", subject=username)
        if not allowed:
            error = rate_error
        else:
            try:
                user = login_user(username, password, ip=client_ip())
            except ValueError as exc:
                error = message_for(str(exc)) or message_for("invalid_credentials")
                user = None
            else:
                if user:
                    start_session(user)
                    return redirect(url_for("dashboard"))
                error = message_for("invalid_credentials")

    return render_template("login.html", error=error, username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if _logged_in():
        return redirect(url_for("dashboard"))

    error = None
    email = username = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        allowed, rate_error = check_rate_limit(client_ip(), "signup", subject=username)
        if not allowed:
            error = rate_error
        else:
            try:
                user = register_user(username, email, password, ip=client_ip())
                start_session(user)
                return redirect(url_for("dashboard"))
            except ValueError as exc:
                error = message_for(str(exc), signup=True) or message_for("signup_failed", signup=True)

    return render_template("signup.html", error=error, email=email, username=username)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"], role=session.get("role", "user"))


@app.route("/admin")
@role_required("admin")
def admin():
    log_event("admin_access", username=session["username"], ip=client_ip(), user_id=session.get("user_id"))
    return render_template("admin.html", username=session["username"])


@app.route("/logout", methods=["POST"])
def logout():
    log_event("logout", username=session.get("username"), ip=client_ip(), user_id=session.get("user_id"))
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, port=int(os.environ.get("PORT", 5001)))
