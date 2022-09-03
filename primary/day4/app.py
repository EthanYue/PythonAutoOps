import os
import time
import json
from hashlib import md5
from functools import wraps
from http import HTTPStatus

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, DateTime, Numeric

app = Flask(__name__)

ACCOUNTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.json")

SESSION_IDS = {}

LOGIN_TIMEOUT = 60 * 60 * 24

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Yfy98333498@127.0.0.1:3306/python_ops?charset=utf8"
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Devices(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `devices` (
        `id` INT AUTO_INCREMENT COMMENT '自增主键',
        `ip` VARCHAR(16) NOT NULL COMMENT 'IP地址',
        `hostname` VARCHAR(128) COMMENT '主机名',
        `idc` VARCHAR(32) COMMENT '机房',
        `row` VARCHAR(8) COMMENT '机柜行',
        `column` VARCHAR(8) COMMENT '机柜列',
        `vendor` VARCHAR(16) COMMENT '厂商',
        `model` VARCHAR(16) COMMENT '型号',
        `role` VARCHAR(8) COMMENT '角色',
        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    """
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    ip = db.Column(db.String(16), nullable=False, comment="IP地址")
    hostname = db.Column(db.String(128), nullable=False, comment="主机名")
    idc = db.Column(db.String(32), comment="机房")
    row = db.Column(db.String(8), comment="机柜行")
    column = db.Column(db.String(8), comment="机柜列")
    vendor = db.Column(db.String(16), comment="厂商")
    model = db.Column(db.String(16), comment="型号")
    role = db.Column(db.String(8), comment="角色")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")

    @classmethod
    def to_model(cls, **kwargs):
        device = Devices()  # 实例化一个device对象
        columns = [c.name for c in cls.__table__.columns]  # 获取Devices模型定义的所有列属性的名字
        for k, v in kwargs.items():  # 遍历传入kwargs的键值
            if k in columns:  # 如果键包含在列名中，则为该device对象赋加对应的属性值
                setattr(device, k, v)
        return device

    def to_dict(self):
        res = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(col.type, DateTime):  # 判断类型是否为DateTime
                if not val:  # 判断实例中该字段是否有值
                    value = ""
                else:  # 进行格式转换
                    value = val.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(col.type, Numeric):  # 判断类型是否为Numeric
                value = float(val)  # 进行格式转换
            else:  # 剩余的直接取值
                value = val
            res[col.name] = value
        return res


def permission(func):
    @wraps(func)
    def inner():
        session_id = request.headers.get("session_id", "")
        global SESSION_IDS
        if session_id not in SESSION_IDS:  # 是否存在会话信息
            return {"data": None, "status_code": "FORBIDDEN", "message": "username not login"}
        if time.time() - SESSION_IDS[session_id]["timestamp"] > LOGIN_TIMEOUT:
            SESSION_IDS.pop(session_id)  # 如果失效则移除会话信息
            return {"data": None, "status_code": "FORBIDDEN", "message": "username login timeout"}
        SESSION_IDS[session_id]["timestamp"] = time.time()  # 更新会话时间
        return func()
    return inner


@app.route("/register", methods=["POST"])
def register():
    """注册用户信息"""
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password: # 判断用户输入的参数
        return {"data": None, "status_code": "InvalidParams", "message": "must have username and password"}
    if not os.path.exists(ACCOUNTS_FILE): # 判断是否存在指定文件
        return {"data": None, "status_code": "NotFound", "message": "not found accounts file"}
    with open("accounts.json", "r+") as f:
        accounts = json.load(f)
    for account in accounts:
        if account["username"] == username: # 判断是否用户已存在
            return {"data": None, "status_code": "Duplicated", "message": "username is already exists"}
    accounts.append({"username": username, "password": md5(password.encode()).hexdigest()})
    with open("accounts.json", "w") as f:
        json.dump(accounts, f)
    return {"data": username, "status_code": "OK", "message": "register username successfully"}


@app.route("/login", methods=["POST"])
def login():
    """用户登录"""
    username = request.form.get("username")
    password = request.form.get("password")
    if not os.path.exists(ACCOUNTS_FILE):  # 是否存在用户信息文件
        return {"data": None, "status_code": "NotFound", "message": "not found accounts file"}
    with open("accounts.json", "r+") as f:
        accounts = json.load(f)
    usernames = [account["username"] for account in accounts]
    if username not in usernames:  # 是否用户已注册
        return {"data": None, "status_code": "NotFound", "message": "username is not exists"}
    for account in accounts:
        if account["username"] == username:
            current_user = account
            if md5(password.encode()).hexdigest() != account["password"]:  # 是否用户名密码正确
                return {"data": None, "status_code": "Unauthorized", "message": "password is not correct"}
            session_id = md5((password + str(time.time())).encode()).hexdigest()  # 生成会话ID
            global SESSION_IDS
            SESSION_IDS[session_id] = {"user_info": current_user, "timestamp": time.time()}  # 记录会话信息
            return {"data": {"session_id": session_id}, "status_code": "OK", "message": "login successfully"}


@app.route("/cmdb/add", methods=["POST"])
def add():
    data = request.get_json()
    device = Devices.to_model(**data)
    db.session.add(device)
    db.session.commit()
    return {"status_code": HTTPStatus.OK}


@app.route("/cmdb/get")
def get():
    """ 查询CMDB """
    devices = Devices.query.all()
    res = []
    for d in devices:
        res.append(d.to_dict())
    return jsonify({"status_code": HTTPStatus.OK, "data": res})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)