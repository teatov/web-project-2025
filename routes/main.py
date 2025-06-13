from flask import Blueprint, abort, render_template, request, send_from_directory
import forms
import upload
import database
import models

blueprint = Blueprint("main", __name__, template_folder="templates")


@blueprint.route("/")
def index():
    db = database.create_session()
    movies = (
        db.query(models.Movie).order_by(models.Movie.created_at.desc()).limit(12).all()
    )

    return render_template("main/index.jinja", movies=movies)


@blueprint.route("/search")
def search():
    query = request.args.get("query")
    genre = request.args.get("genre")
    staff = request.args.get("staff")
    studio = request.args.get("studio")

    db = database.create_session()
    movies = db.query(models.Movie)

    if query:
        movies = movies.filter(models.Movie.title.like(f"%{query}%"))
    if genre:
        movies = movies.filter(models.Movie.genres.any(id=genre))
    if staff:
        movies = movies.filter(models.Movie.staff.any(id=staff))
    if studio:
        movies = movies.filter(models.Movie.studios.any(id=studio))

    movies = movies.order_by(models.Movie.created_at.desc()).all()

    return render_template("main/search.jinja", movies=movies)


@blueprint.route("/movie/<slug>")
def movie(slug: str):
    db = database.create_session()
    movie = db.query(models.Movie).filter(models.Movie.slug == slug).first()

    if not movie:
        abort(404)

    return render_template("main/movie.jinja", movie=movie)


@blueprint.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(upload.UPLOAD_FOLDER, name)
