import time
from datetime import datetime, timedelta

from flask import Blueprint, request, current_app

from junior.flaskProject.application.exception import Success, APIException
from junior.flaskProject.application.services.inspection import InspectionService
from junior.flaskProject.application.models import db
from junior.flaskProject.application.models.action import Action
from junior.flaskProject.application.services.device import DeviceORMHandler
from junior.flaskProject.application.services.action import ActionORMHandler
from junior.flaskProject.application.services.inspection import InspectionORMHandler
from junior.flaskProject.utils import format_time_str

inspection_blueprint = Blueprint("inspection", __name__, url_prefix="/inspection")


@inspection_blueprint.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    inspection = InspectionService(
        config=current_app.config,
        action_handler=ActionORMHandler(db.session()),
        inspection_handler=InspectionORMHandler(db.session()),
        logger=current_app.logger,
    )
    actions = Action.query.filter(Action.id.in_(data.get("action_ids"))).all()
    if not actions:
        raise Exception(f"not found ids {data.get('action_ids')}")
    device_list = DeviceORMHandler(db.session()).get_by_sn(data.get("sn_list", []))
    if not device_list:
        return APIException(message="not found device")
    result = inspection.run(device_list, actions)
    data = {}
    for sn in result:
        data[sn] = [item for item in result[sn]]
    return Success(data=data)


@inspection_blueprint.route("/export", methods=["POST"])
def export():
    data = request.get_json()
    if "start_time" in data:
        start_time = format_time_str(data["start_time"])
    else:
        start_time = datetime.now() - timedelta(days=1)
    if "end_time" in data:
        end_time = format_time_str(data["end_time"])
    else:
        end_time = datetime.now()
    handler = InspectionORMHandler(db.session())
    handler.export(DeviceORMHandler(db.session()), int(start_time.timestamp()), int(end_time.timestamp()))
    return Success()
