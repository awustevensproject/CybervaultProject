import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from auth.login import login_user
from auth.signup import register_user
from config import FLASK_DEBUG, SECRET_KEY, SESSION_COOKIE_SECURE, SESSION_LIFETIME, validate_config
from utils.access import client_ip, login_required, role_required
from utils.csrf import get_csrf_token, validate_csrf_token
from utils.errors import message_for
from utils.password_policy import MAX_PASSWORD_LEN, analyze_password
from utils.rate_limit import check_rate_limit
from utils.security_log import log_event
from utils.session import start_session

validate_config()

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=SESSION_COOKIE_SECURE,
    PERMANENT_SESSION_LIFETIME=SESSION_LIFETIME,
    TEMPLATES_AUTO_RELOAD=FLASK_DEBUG,
)


@app.context_processor
def inject_csrf():
    return {"csrf_token": get_csrf_token()}


@app.after_request
def security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self' https://api.pwnedpasswords.com"
    )
    return response


def _logged_in() -> bool:
    return bool(session.get("username"))


def _csrf_invalid() -> bool:
    token = request.form.get("csrf_token") if request.form else None
    return not validate_csrf_token(token)


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
    success = None
    username = ""

    if session.pop("signup_success", False):
        success = "Account created. Sign in with your username and password."
        username = session.pop("signup_username", "")

    if request.method == "POST":
        if _csrf_invalid():
            error = message_for("csrf_invalid") or "Invalid request. Please try again."
        else:
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

    return render_template("login.html", error=error, success=success, username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if _logged_in():
        return redirect(url_for("dashboard"))

    error = None
    email = username = ""
    password = ""

    if request.method == "POST":
        if _csrf_invalid():
            error = message_for("csrf_invalid", signup=True) or "Invalid request. Please try again."
        else:
            email = request.form.get("email", "").strip()
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            allowed, rate_error = check_rate_limit(client_ip(), "signup", subject=username)
            if not allowed:
                error = rate_error
            else:
                try:
                    user = register_user(username, email, password, ip=client_ip())
                    session["signup_success"] = True
                    session["signup_username"] = user["username"]
                    return redirect(url_for("login"))
                except ValueError as exc:
                    code = str(exc)
                    error = message_for(code, signup=True) or message_for("signup_failed", signup=True)
                    if code == "username_taken":
                        username = ""

    return render_template("signup.html", error=error, email=email, username=username, password=password)


@app.route("/api/password-strength", methods=["POST"])
def password_strength():
    payload = request.get_json(silent=True) or {}
    if not validate_csrf_token(payload.get("csrf_token")):
        return jsonify({"error": "Invalid request."}), 403

    allowed, rate_error = check_rate_limit(client_ip(), "password_strength")
    if not allowed:
        return jsonify({"error": rate_error}), 429

    password = payload.get("password", "")
    if len(password) > MAX_PASSWORD_LEN:
        return jsonify({"error": "Password too long."}), 400

    return jsonify(analyze_password(password))


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
    if not _csrf_invalid():
        log_event("logout", username=session.get("username"), ip=client_ip(), user_id=session.get("user_id"))
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, port=int(os.environ.get("PORT", 5001)))
