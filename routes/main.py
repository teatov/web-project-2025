from flask import Blueprint, abort, redirect, render_template, request, send_from_directory
import forms
import upload
import database
import models
from flask_login import current_user

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
        movies = movies.filter(models.Movie.title.ilike(f"%{query}%"))
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


@blueprint.route("/movie/<slug>/log", methods=["GET", "POST"])
def movie_log(slug: str):
    db = database.create_session()
    movie = db.query(models.Movie).filter(models.Movie.slug == slug).first()

    if not movie:
        abort(404)

    log = (
        db.query(models.UserMovieLog)
        .filter(
            models.UserMovieLog.movie_id == movie.id,
            models.UserMovieLog.user_id == current_user.id,
        )
        .first()
    )

    if not log:
        log = models.UserMovieLog(user_id=current_user.id, movie_id=movie.id)

    form = forms.UserMovieLog(request.form, log)
    if request.method == "POST" and form.validate():
        log.watched = form.watched.data
        log.liked = form.liked.data
        log.watchlist = form.watchlist.data
        log.rating = form.rating.data
        log.review = form.review.data
    
        if not log.created_at:
            db.add(log)
        db.commit()
        return redirect(f"/movie/{movie.slug}")

    return render_template("main/movie-log.jinja", movie=movie, log=log, form=form)


@blueprint.route("/profile/<int:id>")
def profile(id: int):
    db = database.create_session()
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        abort(404)

    return render_template("main/profile.jinja", user=user)


@blueprint.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(upload.UPLOAD_FOLDER, name)
