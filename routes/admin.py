from flask import Blueprint, abort, render_template, redirect, request, url_for
from flask_login import (
    login_required,
    current_user,
)
from slugify import slugify
import forms
import database
import models
from upload import upload_file, delete_file

blueprint = Blueprint("admin", __name__, template_folder="templates")


@blueprint.route("/admin")
@login_required
def admin_index():
    if not current_user.is_admin:
        return redirect("/")

    db = database.create_session()
    movies = db.query(models.Movie).order_by(models.Movie.created_at.desc()).all()

    return render_template("admin/index.jinja", movies=movies)


def movie_info_choice(db):
    countries = (
        db.query(models.MovieCountry).order_by(models.MovieCountry.name.asc()).all()
    )
    countries_choices = [(i.id, i.name) for i in countries]
    return countries_choices


def before_save_movie(movie, form, db):
    with db.no_autoflush:
        if (
            db.query(models.Movie)
            .filter(
                models.Movie.slug == slugify(form.title.data),
                models.Movie.id != movie.id,
            )
            .first()
        ):
            return (
                movie,
                render_template(
                    "admin/movie-form.jinja",
                    form=form,
                    movie=movie,
                    message="Фильм с таким названием уже существует",
                ),
            )

    movie.title = form.title.data
    movie.release_date = form.release_date.data
    movie.description = form.description.data
    movie.set_slug()

    genres = (
        db.query(models.MovieGenre)
        .filter(models.MovieGenre.id.in_([int(i) for i in form.genres.data]))
        .all()
    )
    movie.genres = genres

    studios = (
        db.query(models.MovieStudio)
        .filter(models.MovieStudio.id.in_([int(i) for i in form.studios.data]))
        .all()
    )
    movie.studios = studios

    staff = (
        db.query(models.MovieStaff)
        .filter(models.MovieStaff.id.in_([int(i) for i in form.staff.data]))
        .all()
    )
    movie.staff = staff

    country = (
        db.query(models.MovieCountry)
        .filter(
            models.MovieCountry.id == int(form.country.data),
        )
        .first()
    )
    movie.country = country

    poster_file_url = upload_file(request.files["poster_file"], movie.slug)
    if poster_file_url:
        if movie.poster_file:
            delete_file(movie.poster_file)
        movie.poster_file = poster_file_url

    return (movie, None)


@blueprint.route("/admin/movie-create", methods=["GET", "POST"])
@login_required
def movie_create():
    if not current_user.is_admin:
        return redirect("/")

    db = database.create_session()
    countries_choices = movie_info_choice(db)

    form = forms.Movie(request.form)
    form.country.choices = countries_choices
    if request.method == "POST" and form.validate():

        movie = models.Movie()

        (movie, error_render) = before_save_movie(movie, form, db)
        if error_render:
            return error_render

        db.add(movie)
        db.commit()
        db.refresh(movie)
        return redirect(f"/movie/{movie.slug}")

    return render_template("admin/movie-form.jinja", form=form)


@blueprint.route("/admin/movie-edit/<slug>", methods=["GET", "POST"])
@login_required
def movie_edit(slug: str):
    if not current_user.is_admin:
        return redirect("/")

    db = database.create_session()
    movie = db.query(models.Movie).filter(models.Movie.slug == slug).first()
    countries_choices = movie_info_choice(db)

    if not movie:
        abort(404)

    form = forms.Movie(request.form, movie)
    form.country.choices = countries_choices
    form.country.data = movie.country_id
    if request.method == "POST" and form.validate():
        (movie, error_render) = before_save_movie(movie, form, db)
        if error_render:
            return error_render

        db.commit()
        db.refresh(movie)
        return redirect(f"/movie/{movie.slug}")

    return render_template("admin/movie-form.jinja", form=form, movie=movie)


@blueprint.route("/admin/movie-delete/<int:id>", methods=["POST"])
@login_required
def movie_delete(id: str):
    if not current_user.is_admin:
        return redirect("/")

    db = database.create_session()
    movie = db.query(models.Movie).filter(models.Movie.id == id).first()

    if not movie:
        abort(404)

    if movie.poster_file:
        delete_file(movie.poster_file)
    db.delete(movie)
    db.commit()

    return redirect(f"/admin")


def make_generic_index(
    model, title: str, create_label: str, create_url: str, edit_url: str
):
    def generic_index():
        if not current_user.is_admin:
            return redirect("/")

        db = database.create_session()
        records = db.query(model).all()

        form = forms.GenericRecord(request.form)

        return render_template(
            "admin/generic-records.jinja",
            records=records,
            title=title,
            create_label=create_label,
            create_url=create_url,
            edit_url=edit_url,
            form=form,
        )

    return generic_index


def make_generic_create(model, redirect_url: str, create_title: str):
    def generic_create():
        if not current_user.is_admin:
            return redirect("/")

        form = forms.GenericRecord(request.form)
        if request.method == "POST" and form.validate():
            db = database.create_session()

            record = model(
                name=form.name.data.strip(),
            )

            db.add(record)
            db.commit()
            db.refresh(record)
            return redirect(redirect_url)

        return render_template(
            "admin/generic-record-form.jinja", form=form, create_title=create_title
        )

    return generic_create


def make_generic_edit(model, id: int, redirect_url: str, delete_action: str):
    def generic_edit():
        if not current_user.is_admin:
            return redirect("/")

        db = database.create_session()
        record = db.query(model).filter(model.id == id).first()

        if not record:
            abort(404)

        form = forms.GenericRecord(request.form, record)
        if request.method == "POST" and form.validate():
            record.name = form.name.data.strip()

            db.commit()
            db.refresh(record)
            return redirect(redirect_url)

        return render_template(
            "admin/generic-record-form.jinja",
            form=form,
            record=record,
            delete_action=delete_action,
        )

    return generic_edit


def make_generic_delete(model, id: int, redirect_url: str):
    def generic_delete():
        if not current_user.is_admin:
            return redirect("/")

        db = database.create_session()
        record = db.query(model).filter(model.id == id).first()

        if not record:
            abort(404)

        db.delete(record)
        db.commit()

        return redirect(redirect_url)

    return generic_delete


@blueprint.route("/admin/studios")
@login_required
def studios_index():
    return make_generic_index(
        models.MovieStudio,
        "Студии",
        "Добавить новую студию",
        "/admin/studio-create",
        "/admin/studio-edit",
    )()


@blueprint.route("/admin/studio-create", methods=["GET", "POST"])
@login_required
def studio_create():
    return make_generic_create(models.MovieStudio, "/admin/studios", "Новая студия")()


@blueprint.route("/admin/studio-edit/<int:id>", methods=["GET", "POST"])
@login_required
def studio_edit(id: int):
    return make_generic_edit(
        models.MovieStudio, id, "/admin/studios", "/admin/studio-delete"
    )()


@blueprint.route("/admin/studio-delete/<int:id>", methods=["GET", "POST"])
@login_required
def studio_delete(id: int):
    return make_generic_delete(models.MovieStudio, id, "/admin/studios")()


@blueprint.route("/admin/genres")
@login_required
def genres_index():
    return make_generic_index(
        models.MovieGenre,
        "Жанры",
        "Добавить новый жанр",
        "/admin/genre-create",
        "/admin/genre-edit",
    )()


@blueprint.route("/admin/genre-create", methods=["GET", "POST"])
@login_required
def genre_create():
    return make_generic_create(models.MovieGenre, "/admin/genres", "Новый жанр")()


@blueprint.route("/admin/genre-edit/<int:id>", methods=["GET", "POST"])
@login_required
def genre_edit(id: int):
    return make_generic_edit(
        models.MovieGenre, id, "/admin/genres", "/admin/genre-delete"
    )()


@blueprint.route("/admin/genre-delete/<int:id>", methods=["GET", "POST"])
@login_required
def genre_delete(id: int):
    return make_generic_delete(models.MovieGenre, id, "/admin/genres")()


@blueprint.route("/admin/staff")
@login_required
def staff_index():
    return make_generic_index(
        models.MovieStaff,
        "Персоналии",
        "Добавить новую персоналию",
        "/admin/staff-create",
        "/admin/staff-edit",
    )()


@blueprint.route("/admin/staff-create", methods=["GET", "POST"])
@login_required
def staff_create():
    return make_generic_create(models.MovieStaff, "/admin/staff", "Новая персоналия")()


@blueprint.route("/admin/staff-edit/<int:id>", methods=["GET", "POST"])
@login_required
def staff_edit(id: int):
    return make_generic_edit(
        models.MovieStaff, id, "/admin/staff", "/admin/staff-delete"
    )()


@blueprint.route("/admin/staff-delete/<int:id>", methods=["GET", "POST"])
@login_required
def staff_delete(id: int):
    return make_generic_delete(models.MovieStaff, id, "/admin/staff")()


@blueprint.route("/admin/countries")
@login_required
def countries_index():
    return make_generic_index(
        models.MovieCountry,
        "Страны",
        "Добавить новую страну",
        "/admin/country-create",
        "/admin/country-edit",
    )()


@blueprint.route("/admin/country-create", methods=["GET", "POST"])
@login_required
def country_create():
    return make_generic_create(
        models.MovieCountry, "/admin/countries", "Новая страна"
    )()


@blueprint.route("/admin/country-edit/<int:id>", methods=["GET", "POST"])
@login_required
def country_edit(id: int):
    return make_generic_edit(
        models.MovieCountry, id, "/admin/countries", "/admin/country-delete"
    )()


@blueprint.route("/admin/country-delete/<int:id>", methods=["GET", "POST"])
@login_required
def country_delete(id: int):
    return make_generic_delete(models.MovieCountry, id, "/admin/countries")()
