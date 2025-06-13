from flask import Blueprint, abort, render_template, redirect, request, url_for
from flask_login import (
    login_required,
    current_user,
)
import forms
import database
import models
from upload import upload_file

blueprint = Blueprint("admin", __name__, template_folder="templates")


@blueprint.route("/admin")
@login_required
def admin_index():
    if not current_user.is_admin:
        return redirect("/")

    db = database.create_session()
    movies = db.query(models.Movie).all()

    return render_template("admin/index.jinja", movies=movies)


@blueprint.route("/admin/movie-create", methods=["GET", "POST"])
@login_required
def movie_create():
    if not current_user.is_admin:
        return redirect("/")

    form = forms.Movie(request.form)
    if request.method == "POST" and form.validate():
        db = database.create_session()
        movie = models.Movie(
            title=form.title.data,
            release_date=form.release_date.data,
            description=form.description.data,
        )
        movie.set_slug()

        poster_file_url = upload_file(request.files["poster_file"])
        if poster_file_url:
            movie.poster_file = poster_file_url

        db.add(movie)
        db.commit()
        db.refresh(movie)
        return redirect(f"/movie/{movie.id}")

    return render_template("admin/movie-form.jinja", form=form)


@blueprint.route("/admin/movie-edit/<int:id>", methods=["GET", "POST"])
@login_required
def movie_edit(id: int):
    if not current_user.is_admin:
        return redirect("/")

    db = database.create_session()
    movie = db.query(models.Movie).filter(models.Movie.id == id).first()

    if not movie:
        abort(404)

    form = forms.Movie(request.form, movie)
    if request.method == "POST" and form.validate():
        movie.title = form.title.data
        movie.release_date = form.release_date.data
        movie.description = form.description.data
        movie.set_slug()

        poster_file_url = upload_file(request.files["poster_file"])
        if poster_file_url:
            movie.poster_file = poster_file_url

        db.commit()
        db.refresh(movie)
        return redirect(f"/movie/{movie.id}")

    return render_template("admin/movie-form.jinja", form=form, movie=movie)
