from flask import Flask, render_template
import datetime
import database
import models
from flask_login import LoginManager
import routes
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
login_manager = LoginManager()
login_manager.init_app(app)

app.register_blueprint(routes.blueprint)

database.global_init("_data.db")


def format_date(date: datetime.date) -> str:
    return date.strftime("%d.%m.%Y")


app.jinja_env.globals.update(format_date=format_date)


@login_manager.user_loader
def load_user(user_id):
    db = database.create_session()
    return db.query(models.User).get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template("error.jinja", message="401 Неавторизованный"), 401
