from flask import Flask, request
from cmdb import cmdb_handler, HTTPParams

CMDB_HANDLER = cmdb_handler()

app = Flask(__name__)


@app.route("/cmdb", methods=["POST"])
def cmdb():
    """操作CMDB"""
    try:
        params = HTTPParams(CMDB_HANDLER.operations)
        op, args = params.parse(**request.form)
        ret = CMDB_HANDLER.execute(op, *args)
        return {"data": ret, "status_code": "OK", "message": "operate cmdb success"}
    except Exception as e:
        return {"data": None, "status_code": "Fail", "message": str(e)}


if __name__ == "__main__":
    app.run(port=8080, debug=True)