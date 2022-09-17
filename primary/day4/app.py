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
    __tablename__ = "devices"
    sn = db.Column(db.String(128), primary_key=True, comment="资产号")
    ip = db.Column(db.String(16), nullable=False, comment="IP地址")
    hostname = db.Column(db.String(128), nullable=False, comment="主机名")
    idc = db.Column(db.String(32), comment="机房")
    vendor = db.Column(db.String(16), comment="厂商")
    model = db.Column(db.String(16), comment="型号")
    role = db.Column(db.String(8), comment="角色")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")

    detail = db.relationship("DeviceDetail", uselist=False, backref="device")
    ports = db.relationship("Ports", uselist=True, backref="device")

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


class DeviceDetail(db.Model):
    __tablename = "device_detail"
    sn = db.Column(db.String(128), db.ForeignKey(Devices.sn), primary_key=True, comment="资产号")
    ipv6 = db.Column(db.String(16), nullable=False, comment="IPv6地址")
    console_ip = db.Column(db.String(16), nullable=False, comment="console地址")
    row = db.Column(db.String(8), comment="机柜行")
    column = db.Column(db.String(8), comment="机柜列")
    last_start = db.Column(db.DateTime(), comment="最近启动时间")
    runtime = db.Column(db.Integer, comment="运行时长")
    image_version = db.Column(db.String(128), comment="镜像版本")
    over_warrant = db.Column(db.BOOLEAN, comment="是否过保")
    warrant_time = db.Column(db.DateTime(), comment="过保时间")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")

    @classmethod
    def to_model(cls, **kwargs):
        detail = DeviceDetail()  # 实例化一个device对象
        columns = [c.name for c in cls.__table__.columns]  # 获取Devices模型定义的所有列属性的名字
        for k, v in kwargs.items():  # 遍历传入kwargs的键值
            if k in columns:  # 如果键包含在列名中，则为该device对象赋加对应的属性值
                setattr(detail, k, v)
        return detail

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


class Ports(db.Model):
    __tablename = "ports"
    sn = db.Column(db.String(128), db.ForeignKey(Devices.sn), primary_key=True, comment="资产号")
    port_id = db.Column(db.String(16), nullable=False, primary_key=True, comment="端口ID")
    port_name = db.Column(db.String(64), nullable=False, comment="端口名称")
    port_type = db.Column(db.String(16), comment="端口类型")
    bandwidth = db.Column(db.Integer, comment="端口速率")
    link_status = db.Column(db.String(8), comment="链路状态")
    admin_status = db.Column(db.String(8), comment="管理状态")
    interface_ip = db.Column(db.String(16), comment="端口IP")
    vlan_id = db.Column(db.String(8), comment="端口所属VLAN")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")

    @classmethod
    def to_model(cls, **kwargs):
        port = Ports()  # 实例化一个device对象
        columns = [c.name for c in cls.__table__.columns]  # 获取Devices模型定义的所有列属性的名字
        for k, v in kwargs.items():  # 遍历传入kwargs的键值
            if k in columns:  # 如果键包含在列名中，则为该device对象赋加对应的属性值
                setattr(port, k, v)
        return port

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


@app.route("/cmdb/get_detail")
def get_detail():
    """ 查询设备详情 """
    sn = request.args.get("sn")
    if not sn:
        return jsonify({"status_code": HTTPStatus.BAD_REQUEST, "message": "must have sn arg"})
    try:
        device = Devices.query.filter_by(sn=sn).first()
        if not device:
            return jsonify({"status_code": HTTPStatus.OK, "data": {}})
        res = {**device.to_dict(), **device.detail.to_dict()}  # 通过device类的detail属性获取DeviceDetail的实例
        return jsonify({"status_code": HTTPStatus.OK, "data": res})
    except Exception as e:
        return jsonify({"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": str(e)})


@app.route("/cmdb/add_devices", methods=["POST"])
def add_devices():
    data = request.get_json()
    if not data:
        return jsonify({"status_code": HTTPStatus.BAD_REQUEST, "message": "must have sn arg"})
    if not isinstance(data, list):
        data = [data]
    try:
        devices = []
        for d in data:
            device = Devices.to_model(**d)  # 生成Device模型实例
            device.detail = DeviceDetail.to_model(**d)  # 生成DeviceDetail模型实例，并赋值给device对象
            devices.append(device)  # 插入数据库
        db.session.add_all(devices)
        db.session.commit()
        return jsonify({"status_code": HTTPStatus.OK})
    except Exception as e:
        return jsonify({"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": str(e)})


@app.route("/cmdb/add_ports", methods=["POST"])
def add_ports():
    data = request.get_json()
    if not isinstance(data, list):
        data = [data]
    sns = list(set([p.get("sn", "") for p in data]))  # 获取传入端口参数中的资产号，并去重
    devices = Devices.query.with_entities(Devices.sn).filter(Devices.sn.in_(sns)).all()  # 查询对应资产号的设备
    exists_sn = [d.sn for d in devices]  # 获取数据库中已存在的资产号
    try:
        ports = []
        for p in data:
            if p.get("sn", "") not in exists_sn:  # 如果端口所属的设备不存在，则返回错误
                return jsonify({"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": p.get("sn", "") + " device is not exists"})
            ports.append(Ports.to_model(**p))
        db.session.add_all(ports)
        db.session.commit()
        return jsonify({"status_code": HTTPStatus.OK})
    except Exception as e:
        return jsonify({"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": str(e)})


@app.route("/cmdb/get_ports")
def get_ports():
    """ 查询设备端口 """
    sn = request.args.get("sn")
    if not sn:
        return jsonify({"status_code": HTTPStatus.BAD_REQUEST, "message": "must have sn arg"})
    try:
        device = Devices.query.filter_by(sn=sn).first()
        if not device:
            return jsonify({"status_code": HTTPStatus.OK, "data": {}})
        ports = [p.to_dict() for p in device.ports]
        res = {**device.to_dict(), "ports": ports}
        return jsonify({"status_code": HTTPStatus.OK, "data": res})
    except Exception as e:
        return jsonify({"status_code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": str(e)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)