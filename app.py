from flask import Flask, render_template, request, redirect, url_for
from auth.login import login_user

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # TODO (Day 2): Replace with real authentication logic
        success = login_user(username, password)

        if success:
            return f"Welcome {username}! Login successful (placeholder)."
        else:
            return "Login failed. Invalid credentials."

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)