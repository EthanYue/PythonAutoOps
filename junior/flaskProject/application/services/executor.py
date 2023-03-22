import time
import logging
from typing import Optional, Dict, Union, List
from .action import ActionHandler, Action, CommandType
from .device import DeviceHandler, Device
from netmiko import ConnUnify, BaseConnection


class SSHExecutor:
    def __init__(
            self,
            username: str,
            password: str,
            host: str = "",
            secret: str = "",
            port: str = None,
            device_type: str = "",
            device_condition: Optional[Dict] = None,
            conn_timeout: int = 10,
            auth_timeout: int = None,
            banner_timeout: int = 15,
            logger: Optional[logging.Logger] = None,
            log_file: str = "ssh_executor.log",
            log_level: str = None,
            log_format: str = None,
            action_handler: Optional[ActionHandler] = None,
            device_handler: Optional[DeviceHandler] = None,
            retry_times: int = 3,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.secret = secret
        self.device_type = device_type
        self.conn_timeout = conn_timeout
        self.auth_timeout = auth_timeout
        self.banner_timeout = banner_timeout

        self.action_handler = action_handler
        self.device_handler = device_handler
        if self.host == "":
            self.device = self.fetch_object(device_condition)
            self.host = self.device.ip
            self.port = self.device.channel_port
            self.device_type = self.device.device_type

        self.logger = logger
        if self.logger is None:
            if log_level is None:
                log_level = logging.INFO
            if log_format is None:
                log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"

            logging.basicConfig(filename=log_file, level=log_level, format=log_format)
            self.logger = logging.getLogger(__name__)
        self.retry_times = retry_times
        self.conn = None
        self.result = []

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

    def execute(
            self, action: Optional[Action] = None,
            action_condition: Optional[Dict] = None,
            read_timeout: int = 10, parse: bool = False) -> Union[List, str]:
        action_condition.update({"vendor": self.device.vendor.lower(), "model": self.device.model.lower()})
        if action is None:
            action = self.fetch_action(action_condition)
        if action.type == CommandType.Config:
            output = self.connection.send_config_set(action.cmd, read_timeout=read_timeout)
        else:
            self.connection.enable()
            output = self.connection.send_command(action.cmd, read_timeout=read_timeout)

        parse_result = ""
        if parse:
            parse_result = self.action_handler.parse(self.device_type, action, output)
        self.save(action.cmd, output, parse_result)
        return parse_result if parse_result else output

    def fetch_object(self, condition: Dict) -> Device:
        if self.device_handler is None:
            raise Exception("has no device handler")
        devices = self.device_handler.get(condition)
        if len(devices) == 0:
            raise Exception("has no device")
        if len(devices) > 1:
            self.logger.warning("fetch device more then one")
            # raise Exception()
        return devices[0]

    def fetch_action(self, condition: Dict) -> Action:
        if self.action_handler is None:
            raise Exception("has no action handler")
        actions = self.action_handler.get(condition)
        if len(actions) == 0:
            raise Exception(f"has no action, condition: {condition}")
        if len(actions) > 1:
            # self.logger.warning("fetch action more than one")
            raise Exception("fetch action more then one")
        return actions[0]

    def parse(self):
        pass

    def save(self, cmd: str, output: str, parse_result: str):
        self.result.append({"cmd": cmd, "output": output, "timestamp": time.time(), "parse_result": parse_result})

    def close(self):
        if self.connection is not None:
            self.connection.disconnect()
