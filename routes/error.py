from flask import Blueprint, render_template

blueprint = Blueprint("error", __name__, template_folder="templates")


@blueprint.errorhandler(404)
def page_not_found(_):
    return render_template("error.jinja", message="404 Страница не найдена"), 404


@blueprint.errorhandler(405)
def page_not_found(_):
    return render_template("error.jinja", message="405 Метод не разрешён"), 405
