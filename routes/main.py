from flask import Blueprint, render_template, send_from_directory
import upload

blueprint = Blueprint("main", __name__, template_folder="templates")


@blueprint.route("/")
def index():
    return render_template("index.jinja")


@blueprint.route("/uploads/<name>")
def download_file(name):
    return send_from_directory(upload.UPLOAD_FOLDER, name)
