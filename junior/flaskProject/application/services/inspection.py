import abc
import concurrent.futures
import json
import logging
import csv
import traceback
from datetime import datetime
from typing import Any, List, Dict
from flask import Config
from concurrent.futures.thread import ThreadPoolExecutor

from sqlalchemy.orm import scoped_session
from sqlalchemy import and_

from junior.flaskProject.application.services.executor import SSHExecutor
from junior.flaskProject.utils import format_time
from junior.flaskProject.application.models.inspection import Inspection as InspectionModel
from junior.flaskProject.application.services.action import ActionHandler
from junior.flaskProject.application.services.device import DeviceHandler, Device


class InspectionHandler(abc.ABC):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def add(self, data: List[Dict]) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def execute(cls, device: Device, actions: List[Any], config: Dict, action_handler: ActionHandler, logger: logging.Logger) -> List[Dict]:
        pass

    @abc.abstractmethod
    def export(self, device_handler: DeviceHandler, start_time: int, end_time: int) -> None:
        pass


class InspectionORMHandler(InspectionHandler):

    def __init__(self, db_handler: scoped_session):
        self.db_handler = db_handler

    def add(self, data: List[Dict]):
        if self.db_handler is None:
            raise Exception("has no active db handler")
        result = []
        for item in data:
            result.append(InspectionModel.to_model(**item))
        self.db_handler.add_all(result)
        self.db_handler.commit()

    @staticmethod
    def check_version(result: List[Dict]) -> List[Dict]:
        pass

    @classmethod
    def execute(cls, device: Device, actions: List[Any], config: Dict, action_handler: ActionHandler, logger: logging.Logger) -> List[Dict]:
        result = []
        try:
            with SSHExecutor(
                    username=config.get("SSH_USERNAME"),
                    password=config.get("SSH_PASSWORD"),
                    secret=config.get("SSH_SECRET"),
                    device=device,
                    logger=logger) as ssh:
                for action in actions:
                    ssh.execute(action=action, action_handler=action_handler, parse=True)
                    ssh_result = ssh.result
            for res in ssh_result:
                validation_func = None
                if hasattr(cls, res["action"].name):
                    validation_func = getattr(cls, res["action"].name)
                validation_result = validation_func(res["parse_result"]) if validation_func else res["parse_result"]
                result.append({
                    "action_id": res["action"].id,
                    "output": res["output"],
                    "parse_result": res["parse_result"],
                    "validation_result": validation_result,
                })
        except Exception:
            logger.error(f"execute {device.hostname} failed, err: {traceback.format_exc()}")
        return result

    def export(self, device_handler: DeviceHandler, start_time: datetime, end_time: datetime) -> None:
        data = InspectionModel.query \
            .filter(
                and_(InspectionModel.timestamp > start_time, InspectionModel.timestamp < end_time)) \
            .all()
        device_list = device_handler.get_by_sn([item.sn for item in data])
        sn_map = {item.sn: item for item in device_list}
        header = {"hostname"}
        device_result = {}
        for result in data:
            device = sn_map.get(result.sn)
            if not device:
                continue
            try:
                result_dict = json.loads(result.validation_result)
            except Exception:
                pass
                continue
            for col in result_dict[0].keys():
                header.add(col)
            for row in result_dict:
                device_result.setdefault(device.hostname, {}).update(row)

        with open(f"export_{format_time(0)}.csv", "w+") as f:
            writer = csv.DictWriter(f, fieldnames=list(header))
            writer.writeheader()
            for hostname in device_result:
                writer.writerows([{"hostname": hostname, **device_result[hostname]}])


class InspectionService:
    def __init__(
            self,
            config: Config,
            action_handler: ActionHandler,
            inspection_handler: InspectionHandler,
            logger: logging.Logger,
            max_workers: int = 8) -> None:
        self.config = config
        self.action_handler = action_handler
        self.inspection_handler = inspection_handler
        self.logger = logger
        self.max_workers = max_workers
        self.result: Dict[str, List[Dict]] = {}

    def run(self, device_list: List[Device], actions: List[Any]) -> Dict[str, List[Dict]]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            for device in device_list:
                future: concurrent.futures.Future = pool.submit(
                    self.inspection_handler.execute, device, actions, self.config, self.action_handler, self.logger)
                future.sn = device.sn
                future.add_done_callback(self.execute_callback)
        self.save()
        return self.result

    def execute_callback(self, future: concurrent.futures.Future):
        self.result[future.sn] = future.result()

    def save(self):
        data = []
        for sn, res in self.result.items():
            for content in res:
                for k in content:
                    if isinstance(content[k], list) or isinstance(content[k], dict):
                        content[k] = json.dumps(content[k], ensure_ascii=False)
                data.append({"sn": sn, **content})
        self.inspection_handler.add(data)
