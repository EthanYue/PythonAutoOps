import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from .models import db
from .views import cmdb_blueprint, action_blueprint, executor_blueprint, inspection_blueprint
from .exception import register_errors
from junior.flaskProject.config import config_mapper


def create_app(env: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_mapper[env])
    db.init_app(app)
    blueprints = [cmdb_blueprint, action_blueprint, executor_blueprint, inspection_blueprint]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    register_logging(app)
    register_errors(app)
    return app


def register_logging(app):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s P[%(process)d] T[%(thread)d] %(lineno)sL@%(filename)s:'
        ' %(message)s')

    handler = RotatingFileHandler("flask.log", maxBytes=1024000, backupCount=10)
    handler.setLevel(app.config.get("LOG_LEVEL"))
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    @app.before_request
    def log_each_request():
        app.logger.info(f"[{request.method}]{request.path} from {request.remote_addr}, params "
                        f"{request.args.to_dict()}, body {request.get_data()}")