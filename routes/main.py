from flask import Blueprint, render_template, request, send_from_directory
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

    if not query:
        return render_template("main/search.jinja", movies=[], query=query)

    db = database.create_session()
    movies = (
        db.query(models.Movie)
        .filter(models.Movie.title.like(f"%{query}%"))
        .order_by(models.Movie.created_at.desc())
        .all()
    )

    return render_template("main/search.jinja", movies=movies, query=query)


@blueprint.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(upload.UPLOAD_FOLDER, name)
