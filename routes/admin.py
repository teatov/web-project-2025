from flask import Blueprint, render_template, redirect
from flask_login import (
    login_required,
    current_user,
)

blueprint = Blueprint("admin", __name__, template_folder="templates")


@blueprint.route("/admin")
@login_required
def admin_index():
    if not current_user.is_admin:
        return redirect("/")

    return render_template("admin/index.jinja")
