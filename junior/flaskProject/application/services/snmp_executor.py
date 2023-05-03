import logging
from typing import Optional, Dict, List, Union, Any
from .action import ActionHandler, Action, CommandType
from easysnmp import Session, SNMPVariable
from .device import Device
from junior.flaskProject.application.services.executor import Executor


class SNMPExecutor(Executor):

    SNMP_Version = 2
    SNMP_Port = 161

    def __init__(
            self,
            community: str,
            device: Device,
            timeout: int = 10,
            logger: Optional[logging.Logger] = None,
            log_file: str = "snmp.log",
            log_level: str = logging.INFO,
            log_format: str = "%(asctime)s %(levelname)s %(name)s %(message)s",
            retry_times: int = 3):
        self.device = device
        self.host = self.device.ip
        self.session = Session(
            hostname=self.device.ip, version=self.SNMP_Version, community=community,
            timeout=timeout, retries=retry_times, remote_port=self.SNMP_Port)

        self.logger = logger
        if self.logger is None:
            logging.basicConfig(filename=log_file, level=log_level, format=log_format)
            self.logger = logging.getLogger(__name__)

        self.result: List[Dict] = []

    def __enter__(self) -> "SNMPExecutor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(exc_type)
            self.logger.error(exc_val)
            self.logger.error(exc_tb)

    def execute(self, action: Action, last_variables: Optional[List[SNMPVariable]]) -> List[SNMPVariable]:
        if ".0" in action.cmd:
            output = [self.session.get(action.cmd)]
        else:
            output = self.session.bulkwalk(action.cmd)
        return self.parse(output, last_variables)

    def parse(self, current_variables: List[SNMPVariable], last_variables: List[SNMPVariable]) -> List[SNMPVariable]:
        oid_idx_map = {item.oid_index: item for item in current_variables}
        last_oid_idx_map = {item.oid_index: item for item in last_variables}
        for idx in oid_idx_map:
            if oid_idx_map[idx].snmp_type == "COUNTER":
                if idx not in last_oid_idx_map:
                    self.logger.error(f"not found oid index {idx} in last_variable")
                    continue
                oid_idx_map[idx].value -= last_oid_idx_map[idx].value
        return list(oid_idx_map.values())

    def save(self):
        pass
