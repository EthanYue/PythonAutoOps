from flask import Blueprint
from ..models import db
from ..services import ActionORMHandler

action_blueprint = Blueprint("action", __name__, url_prefix="/action")


@action_blueprint.route("/get")
def get():
    res = ActionORMHandler(db_handler=db).get()
    return [item.to_dict() for item in res]
