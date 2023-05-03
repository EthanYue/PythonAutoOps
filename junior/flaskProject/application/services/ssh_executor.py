import logging
from typing import Optional, Dict, List, Union, Any
from .action import ActionHandler, Action, CommandType
from .device import Device
from netmiko import ConnUnify, BaseConnection
from junior.flaskProject.application.services.executor import Executor


class SSHExecutor(Executor):

    def __init__(
            self,
            username: str,
            password: str,
            device: Device,
            secret: str = "",
            conn_timeout: int = 10,
            auth_timeout: int = None,
            banner_timeout: int = 15,
            logger: Optional[logging.Logger] = None,
            log_file: str = "ssh_executor.log",
            log_level: str = logging.INFO,
            log_format: str = "%(asctime)s %(levelname)s %(name)s %(message)s",
            retry_times: int = 3,
    ) -> None:
        self.username = username
        self.password = password
        self.secret = secret
        self.conn_timeout = conn_timeout
        self.auth_timeout = auth_timeout
        self.banner_timeout = banner_timeout
        self.device = device
        self.host = self.device.ip
        self.port = self.device.channel_port
        self.device_type = self.device.device_type

        self.logger = logger
        if self.logger is None:
            logging.basicConfig(filename=log_file, level=log_level, format=log_format)
            self.logger = logging.getLogger(__name__)
        self.retry_times = retry_times
        self.conn = None
        self.result: List[Dict] = []

    @property
    def connection(self) -> BaseConnection:
        if not self.conn or not self.conn.is_alive():
            self.conn = self.connect(self.retry_times)
        return self.conn

    def connect(self, retry: int) -> BaseConnection:
        if retry == 0:
            raise Exception("Retry to connect over maximum")
        try:
            conn = ConnUnify(host=self.host, port=self.port, username=self.username, password=self.password,
                             secret=self.secret, device_type=self.device_type, conn_timeout=self.conn_timeout,
                             auth_timeout=self.auth_timeout, banner_timeout=self.banner_timeout, session_log="netmiko.log",
                             session_log_file_mode="append")
            msg = f"Netmiko connection successful to {self.host}:{self.port}"
            self.logger.info(msg)
            return conn
        except Exception as e:
            self.logger.error(str(e))
            return self.connect(retry - 1)

    def __enter__(self) -> "SSHExecutor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(exc_type)
            self.logger.error(exc_val)
            self.logger.error(exc_tb)
        self.close()

    def execute(self, action: Action, read_timeout: int = 10, action_handler: Optional[ActionHandler] = None, parse: bool = False) -> Union[List, str]:
        if action.type == CommandType.Config:
            output = self.connection.send_config_set(action.cmd, read_timeout=read_timeout)
        else:
            self.connection.enable()
            output = self.connection.send_command(action.cmd, read_timeout=read_timeout)

        parse_result = None
        if parse:
            parse_result = action_handler.parse(self.device_type, action, output)
        self.save(action, output, parse_result)
        return parse_result if parse_result else output

    def parse(self):
        pass

    def save(self, action: Action, output: str, parse_result: Optional[Any]):
        self.result.append({"action": action, "output": output, "parse_result": parse_result})

    def close(self):
        if self.connection is not None:
            self.connection.disconnect()
