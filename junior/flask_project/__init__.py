from flask import Flask
from .models import db
from .views import cmdb_blueprint, action_blueprint
from config import config_mapper


def create_app(env: str = "dev") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_mapper[env])
    db.init_app(app)
    blueprints = [cmdb_blueprint, action_blueprint]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    return app
