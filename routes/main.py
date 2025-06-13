from flask import Blueprint, render_template, send_from_directory
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

    return render_template("index.jinja", movies=movies)


@blueprint.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(upload.UPLOAD_FOLDER, name)
