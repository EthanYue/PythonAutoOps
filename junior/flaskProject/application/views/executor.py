from flask import Blueprint, request, current_app
from ..models import db, Action
from ..services import DeviceORMHandler, ActionORMHandler, SSHExecutor
from ..exception import Success, ExecutorError, APIException

executor_blueprint = Blueprint("executor", __name__, url_prefix="/executor")


@executor_blueprint.route("/prompt", methods=["POST"])
def get_prompt():
    data = request.get_json()
    device_handler = DeviceORMHandler(db.session())
    action_handler = ActionORMHandler(db.session())
    devices = device_handler.get(data.get("device_condition"))
    if not devices:
        raise APIException(message="not found device")
    try:
        with SSHExecutor(
                username=current_app.config.get("SSH_USERNAME"),
                password=current_app.config.get("SSH_PASSWORD"),
                secret=current_app.config.get("SSH_SECRET"),
                device=devices[0],
                action_handler=action_handler,
                logger=current_app.logger) as ssh:
            prompt = ssh.conn.base_prompt
        return Success(data=prompt)
    except Exception as e:
        raise ExecutorError(message=str(e))


@executor_blueprint.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()
    try:
        device_condition = data.get("device_condition")
        action_condition = data.get("action_condition")
        action = None
        if "action" in data:
            action = Action.to_model(**data.get("action"))
        device = DeviceORMHandler(db.session()).get(device_condition)
        if not device:
            raise APIException(message="not found device")
        action_handler = ActionORMHandler(db.session())
        with SSHExecutor(
                username=current_app.config.get("SSH_USERNAME"),
                password=current_app.config.get("SSH_PASSWORD"),
                secret=current_app.config.get("SSH_SECRET"),
                device=device[0],
                action_handler=action_handler,
                logger=current_app.logger) as ssh:
            output = ssh.execute(action=action, action_condition=action_condition, parse=data.get("parse", False))
            return Success(data=output)
    except Exception as e:
        raise ExecutorError(message=str(e))
