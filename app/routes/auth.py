from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("/register", methods=["GET", "POST"])
def auth_register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Такой email уже зарегистрирован", "error")
            return redirect(url_for("auth.register"))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Регистрация успешна!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth.route("/login", methods=["GET", "POST"])
def auth_login():
    return render_template("auth/login.html")
