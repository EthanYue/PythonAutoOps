from typing import Dict
from sqlalchemy import text
from junior.flaskProject.utils import to_model as tm, to_dict as td
from . import db


class Inspection(db.Model):
    __tablename__ = "inspection"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sn = db.Column(db.String(64), nullable=False, comment="设备资产号")
    action_id = db.Column(db.Integer, comment="巡检项id")
    output = db.Column(db.Text, comment="执行输出")
    parse_result = db.Column(db.Text, comment="解析结果")
    validation_result = db.Column(db.Text, comment="验证结果")
    timestamp = db.Column(db.Integer, nullable=False, server_default=text('NOW()'), comment="创建时间")

    @classmethod
    def to_model(cls, **kwargs) -> "Inspection":
        return tm(cls, **kwargs)

    def to_dict(self) -> Dict:
        return td(self)
