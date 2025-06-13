import os
from flask import url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "avif"}
UPLOAD_FOLDER = "./uploads"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file, filename):
    if file.filename == "" or not file or not allowed_file(file.filename):
        return None

    filename = filename + "." + secure_filename(file.filename).split(".")[-1]
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return filename


def delete_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    os.remove(path)
