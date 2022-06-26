from flask import Flask, request
from cmdb import cmdb_handler

CMDB_HANDLER = cmdb_handler()

app = Flask(__name__)


@app.route("/")
def index():
    return "hello world"


@app.route("/get", methods=["GET"])
def get():
    """查询CMDB"""
    path = request.args.get("path", "/")
    ret = CMDB_HANDLER.execute("get", [path])
    return ret


@app.route("/init", methods=["POST"])
def init():
    """初始化地域"""
    data = request.get_json()
    region = data.get("region", "")
    ret = CMDB_HANDLER.execute("init", [region])
    return ret


if __name__ == "__main__":
    app.run(port=8080, debug=True)