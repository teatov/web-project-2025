from flask import Flask, render_template
import datetime
import database
import models
from flask_login import LoginManager
import routes.admin
import routes.main
import routes.auth
import upload
import resources
from flask_restful import Api

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.config["UPLOAD_FOLDER"] = upload.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1000 * 1000
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)

app.register_blueprint(routes.main.blueprint)
app.register_blueprint(routes.auth.blueprint)
app.register_blueprint(routes.admin.blueprint)

database.global_init("_data.db")


def format_date(date: datetime.date) -> str:
    return date.strftime("%d.%m.%Y")


def format_year(date: datetime.date) -> str:
    return date.strftime("%Y")


app.jinja_env.globals.update(format_date=format_date)
app.jinja_env.globals.update(format_year=format_year)


@login_manager.user_loader
def load_user(user_id):
    db = database.create_session()
    return db.query(models.User).get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template("error.jinja", message="401 Неавторизованный"), 401


@app.errorhandler(404)
def page_not_found(_):
    return render_template("error.jinja", message="404 Страница не найдена"), 404


@app.errorhandler(405)
def page_not_found(_):
    return render_template("error.jinja", message="405 Метод не разрешён"), 405


api.add_resource(resources.Genre, "/api/genres/<search>")
api.add_resource(resources.Studio, "/api/studios/<search>")
api.add_resource(resources.Staff, "/api/staff/<search>")
