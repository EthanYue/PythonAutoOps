import json
import traceback
from typing import List, Tuple
from flask import Flask, request
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    code = 500
    message = 'API Exception'
    data = None

    def __init__(self, code=None, message=None, data=None):
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message
        if data is not None:
            self.data = data

        super(APIException, self).__init__(self.message, None)

    def get_body(self, environ=None, scope=None) -> str:
        body = {
            "data": self.data,
            "status_code": self.code,
            "message": self.message,
            "request": request.method + ' ' + self.get_url_without_param()
        }
        return json.dumps(body)

    def get_headers(self, environ=None, scope=None) -> List[Tuple[str, str]]:
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_without_param() -> str:
        full_url = str(request.full_path)
        return full_url.split('?')[0]


def register_errors(app: Flask):
    @app.errorhandler(Exception)
    def framework_error(e):
        app.logger.error(str(e))
        app.logger.error(traceback.format_exc())
        if isinstance(e, APIException):  # 手动触发的异常
            return e
        elif isinstance(e, HTTPException):  # 代码异常
            return APIException(e.code, e.description, None)
        else:
            if app.config['DEBUG']:
                raise e
            else:
                return ServerError(message=str(e))


class Success(APIException):
    code = 200
    message = "success"

    def __init__(self, data=None):
        super().__init__(self.code, self.message, data)


class ServerError(APIException):
    code = 500
    message = "server error"


class DBError(APIException):
    code = 510
    message = "db error"


class ExecutorError(APIException):
    code = 520
    message = "executor error"
