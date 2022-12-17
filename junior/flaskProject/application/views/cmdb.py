from flask import Blueprint, request
from ..models import db
from ..services import DeviceORMHandler
from ..exception import Success, DBError

cmdb_blueprint = Blueprint("cmdb", __name__, url_prefix="/cmdb")


@cmdb_blueprint.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    _db = db.session()
    try:
        DeviceORMHandler(_db).add(data)
        return Success()
    except Exception as e:
        _db.rollback()
        raise DBError(message=str(e))


@cmdb_blueprint.route("/delete", methods=["POST"])
def delete():
    data = request.get_json()
    _db = db.session()
    try:
        DeviceORMHandler(_db).delete(data)
        return Success()
    except Exception as e:
        _db.rollback()
        raise DBError(message=str(e))


@cmdb_blueprint.route("/update", methods=["POST"])
def update():
    data = request.get_json()
    _db = db.session()
    try:
        DeviceORMHandler(db.session()).update(data)
        return Success()
    except Exception as e:
        _db.rollback()
        raise DBError(message=str(e))


@cmdb_blueprint.route("/get")
def get():
    try:
        res = DeviceORMHandler(db.session()).get()
        return Success(data=[item.to_dict() for item in res])
    except Exception as e:
        raise DBError(message=str(e))

