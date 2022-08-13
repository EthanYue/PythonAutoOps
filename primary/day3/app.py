import os
import time
import json
from enum import Enum
from hashlib import md5
from functools import wraps
from http import HTTPStatus
from flask import Flask, request

app = Flask(__name__)

ACCOUNTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.json")

SESSION_IDS = {}

LOGIN_TIMEOUT = 60 * 60 * 24


class Role(Enum):
    ADMIN = "admin"
    CMDB = "cmdb"
    GUEST = "guest"


def permission(permit_roles):
    def login_required(func):
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
            current_user = SESSION_IDS[session_id]
            role_values = [role.value for role in permit_roles]
            if permit_roles is not None and current_user["user_info"].get("role") not in role_values:
                return {"data": None, "status_code": HTTPStatus.FORBIDDEN, "message": "user has no permission"}
            return func()
        return inner
    return login_required


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


@app.route("/cmdb", methods=["POST"])
@permission([Role.ADMIN])
def index():
    pass
    return "success"


@app.route("/permission_manage", methods=["POST"])
@permission([Role.ADMIN])
def permission_manage():
    username = request.form.get("username")
    role = request.form.get("role")
    if not username or not role:
        return {"data": None, "status_code": HTTPStatus.BAD_REQUEST}
    roles = [role.value for role in Role]
    if role not in roles:  # 判断输入的角色名称是否合法
        return {"data": None, "status_code": HTTPStatus.BAD_REQUEST}
    if not os.path.exists(ACCOUNTS_FILE): # 是否存在用户信息文件
        return {"data": None, "status_code": HTTPStatus.NOT_FOUND, "message": "not found accounts file"}
    with open("accounts.json", "r+") as f:
        accounts = json.load(f)
    permit_user = None
    for account in accounts:  # 查找被授权用户
        if account.get("username", "") == username:
            permit_user = account
            break
    if permit_user is None:  # 是否用户已注册
        return {"data": None, "status_code": HTTPStatus.NOT_FOUND, "message": "username is not exists"}
    permit_user["role"] = role
    global SESSION_IDS
    for _, session_info in SESSION_IDS.items():  # 如果授权用户已登陆则修改session中该用户的角色信息
        if session_info["user_info"].get("username") == username:
            session_info["user_info"]["role"] = role
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)
    return {"data": "", "status_code": HTTPStatus.OK, "message": "successfully"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)