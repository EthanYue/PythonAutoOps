from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from .action import Action
from .device import Devices, DeviceDetail, Ports