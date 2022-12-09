from flask import Blueprint, request
from ..models import db
from ..services import DeviceORMHandler

cmdb_blueprint = Blueprint("cmdb", __name__, url_prefix="/cmdb")


@cmdb_blueprint.route("/get")
def get():
    res = DeviceORMHandler(db.session()).get()
    return [item.to_dict() for item in res]


@cmdb_blueprint.route("/update", methods=["POST"])
def update():
    data = request.get_json()
    DeviceORMHandler(db.session()).update(data)
    return "success"


@cmdb_blueprint.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    DeviceORMHandler(db.session()).add(data)
    return "success"
