from flask import Blueprint, render_template, redirect, request
import database
import models
import forms
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user,
)

blueprint = Blueprint("auth", __name__, template_folder="templates")


@blueprint.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect("/")

    form = forms.SignUp(request.form)
    if request.method == "POST" and form.validate():
        if form.password.data != form.password_confirm.data:
            return render_template(
                "auth/signup.jinja", form=form, message="Пароли не совпадают"
            )
        db = database.create_session()
        if db.query(models.User).filter(models.User.email == form.email.data).first():
            return render_template(
                "auth/signup.jinja", form=form, message="Эта электропочта уже занята"
            )
        user = models.User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.add(user)
        db.commit()
        return redirect("/login")

    return render_template("auth/signup.jinja", form=form)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = forms.LogIn(request.form)
    if request.method == "POST" and form.validate():
        db = database.create_session()
        user = (
            db.query(models.User).filter(models.User.email == form.email.data).first()
        )
        if not user or not user.check_password(form.password.data):
            return render_template(
                "auth/login.jinja", form=form, message="Некорректная электропочта или пароль"
            )
        login_user(user, remember=form.remember_me.data)
        return redirect("/")

    return render_template("auth/login.jinja", form=form)


@blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")
