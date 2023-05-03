from enum import Enum
from typing import Dict
from junior.flaskProject.utils import to_model as tm, to_dict as td
from junior.flaskProject.application.models import db


class ParseTypeEnum(str, Enum):
    TextFSM = "textfsm"
    Regexp = "regexp"


class Action(db.Model):
    __tablename__ = "action"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False, comment="动作名称")
    description = db.Column(db.String(256), comment="动作描述")
    vendor = db.Column(db.String(64), comment="厂商")
    model = db.Column(db.String(64), comment="型号")
    cmd = db.Column(db.String(256), nullable=False, comment="命令行")
    type = db.Column(db.String(8), comment="命令类型[show|config]")
    parse_type = db.Column(db.String(8), comment="解析类型[regexp|textfsm]")
    parse_content = db.Column(db.Text, comment="解析内容")

    @classmethod
    def to_model(cls, **kwargs) -> "Action":
        return tm(cls, **kwargs)

    def to_dict(self) -> Dict:
        return td(self)


