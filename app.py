from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pyotp
import os


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-in-production"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    two_factor_secret = db.Column(
        db.String(32),
        nullable=True
    )

    two_factor_enabled = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )


with app.app_context():
    db.create_all()


@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return redirect(url_for("register"))

        if len(username) < 3:

            flash(
                "Username must contain at least 3 characters.",
                "error"
            )

            return redirect(url_for("register"))

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

            return redirect(url_for("register"))

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(url_for("register"))

        password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        new_user = User(
            username=username,
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return redirect(url_for("login"))

        user = User.query.filter_by(
            username=username
        ).first()

        if not user or not bcrypt.check_password_hash(
            user.password_hash,
            password
        ):

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(url_for("login"))

        session.clear()

        session["pending_user_id"] = user.id
        session["pending_username"] = user.username

        if user.two_factor_enabled:

            return redirect(
                url_for("verify_2fa")
            )

        session["user_id"] = user.id
        session["username"] = user.username

        session.pop("pending_user_id", None)
        session.pop("pending_username", None)

        return redirect(
            url_for("dashboard")
        )

    return render_template("login.html")


@app.route("/setup-2fa", methods=["GET", "POST"])
def setup_2fa():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(url_for("login"))

    user = db.session.get(
        User,
        session["user_id"]
    )

    if not user:
        session.clear()

        return redirect(url_for("login"))

    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()

        if not code:

            flash(
                "Please enter the verification code.",
                "error"
            )

            return redirect(url_for("setup_2fa"))

        if user.two_factor_secret:

            totp = pyotp.TOTP(
                user.two_factor_secret
            )

            if totp.verify(code):

                user.two_factor_enabled = True

                db.session.commit()

                flash(
                    "Two-factor authentication enabled successfully.",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

            flash(
                "Invalid verification code.",
                "error"
            )

            return redirect(
                url_for("setup_2fa")
            )

        secret = pyotp.random_base32()

        user.two_factor_secret = secret

        db.session.commit()

        return redirect(
            url_for("setup_2fa")
        )

    if not user.two_factor_secret:

        user.two_factor_secret = pyotp.random_base32()

        db.session.commit()

    issuer = "Thiranex Secure Login"

    otp_uri = pyotp.TOTP(
        user.two_factor_secret
    ).provisioning_uri(
        name=user.username,
        issuer_name=issuer
    )

    return render_template(
        "setup_2fa.html",
        secret=user.two_factor_secret,
        otp_uri=otp_uri
    )


@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():

    if "pending_user_id" not in session:

        return redirect(url_for("login"))

    user = db.session.get(
        User,
        session["pending_user_id"]
    )

    if not user or not user.two_factor_enabled:

        session.clear()

        return redirect(url_for("login"))

    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()

        totp = pyotp.TOTP(
            user.two_factor_secret
        )

        if totp.verify(code):

            session["user_id"] = user.id
            session["username"] = user.username

            session.pop("pending_user_id", None)
            session.pop("pending_username", None)

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid or expired 2FA code.",
            "error"
        )

    return render_template(
        "verify_2fa.html",
        username=user.username
    )


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        flash(
            "Please login to access the dashboard.",
            "error"
        )

        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("login"))


if __name__ == "__main__":

    app.run(
        debug=True
    )