from flask import Blueprint, request
from ..models import db
from ..services import ActionORMHandler
from ..exception import Success, DBError

action_blueprint = Blueprint("action", __name__, url_prefix="/action")


@action_blueprint.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    _db = db.session()
    try:
        ActionORMHandler(_db).add(data)
        return Success()
    except Exception as e:
        _db.rollback()
        raise DBError(message=str(e))


@action_blueprint.route("delete", methods=["POST"])
def delete():
    data = request.get_json()
    _db = db.session()
    try:
        ActionORMHandler(db.session()).delete(data)
        return Success()
    except Exception as e:
        _db.rollback()
        raise DBError(message=str(e))


@action_blueprint.route("update", methods=["POST"])
def update():
    data = request.get_json()
    _db = db.session()
    try:
        ActionORMHandler(db.session()).update(data)
        return Success()
    except Exception as e:
        _db.rollback()
        raise DBError(message=str(e))


@action_blueprint.route("/get")
def get():
    args = request.args.to_dict()
    try:
        res = ActionORMHandler(db.session()).get(args)
        return Success(data=[item.to_dict() for item in res])
    except Exception as e:
        raise DBError(message=str(e))

