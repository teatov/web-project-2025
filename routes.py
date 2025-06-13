from flask import Blueprint, render_template, redirect, request, abort
import database
import models
import forms
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user,
)

blueprint = Blueprint("blueprint", __name__, template_folder="templates")


@blueprint.route("/")
def index():
    return render_template("index.jinja")


@blueprint.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect("/")

    form = forms.SignUp(request.form)
    if request.method == "POST" and form.validate():
        if form.password.data != form.password_confirm.data:
            return render_template(
                "signup.jinja", form=form, message="Пароли не совпадают"
            )
        db = database.create_session()
        if db.query(models.User).filter(models.User.email == form.email.data).first():
            return render_template(
                "signup.jinja", form=form, message="Эта электропочта уже занята"
            )
        user = models.User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.add(user)
        db.commit()
        return redirect("/login")

    return render_template("signup.jinja", form=form)


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
                "login.jinja", form=form, message="Некорректная электропочта или пароль"
            )
        login_user(user, remember=form.remember_me.data)
        return redirect("/")

    return render_template("login.jinja", form=form)


@blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")


@blueprint.errorhandler(404)
def page_not_found(_):
    return render_template("error.jinja", message="404 Страница не найдена"), 404


@blueprint.errorhandler(405)
def page_not_found(_):
    return render_template("error.jinja", message="405 Метод не разрешён"), 405
