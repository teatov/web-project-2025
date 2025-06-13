from flask_restful import Resource, abort
import database
import models
from flask import jsonify


def find_or_abort(model, search: str):
    db = database.create_session()
    records = (
        db.query(model)
        .filter(model.name.ilike(f"%{search}%"))
        .order_by(model.name.asc())
        .all()
    )
    return records


default_fields = ["id", "name"]


class Genre(Resource):
    def get(self, search):
        records = find_or_abort(models.MovieGenre, search)
        return jsonify(models.MovieGenre.serialize_list(records, default_fields))


class Studio(Resource):
    def get(self, search):
        records = find_or_abort(models.MovieStudio, search)
        return jsonify(models.MovieStudio.serialize_list(records, default_fields))


class Staff(Resource):
    def get(self, search):
        records = find_or_abort(models.MovieStaff, search)
        return jsonify(models.MovieStaff.serialize_list(records, default_fields))
