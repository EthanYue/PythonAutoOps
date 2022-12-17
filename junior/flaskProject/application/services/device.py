import os
import json
import abc
from typing import List, Dict, Optional
from sqlalchemy.orm import scoped_session
from ..models import Devices, DeviceDetail


class CommandType:
    Show = "show"
    Config = "config"


class Device:
    ip = ""
    hostname = ""
    vendor = ""
    model = ""
    hardware = ""
    channel = "ssh"
    channel_port = 22
    device_type = ""

    @classmethod
    def to_model(cls, **kwargs):
        device = cls()
        for k, v in kwargs.items():
            if hasattr(device, k):
                setattr(device, k, v)
        if device.channel == "telnet":
            device.channel_port = 23
        return device

    def __str__(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_model(cls, model: Devices) -> "Device":
        device = cls()
        for col in [*model.__table__.columns, *model.detail.__table__.columns]:
            if hasattr(device, col.name):
                if col.table.name == model.__tablename__:
                    val = getattr(model, col.name)
                else:
                    val = getattr(model.detail, col.name)
                setattr(device, col.name, val)
        return device


class DeviceHandler(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def add(self, data: List[Dict]) -> None:
        pass

    @abc.abstractmethod
    def delete(self, data: Dict) -> None:
        pass

    @abc.abstractmethod
    def update(self, data: Dict) -> None:
        pass

    @abc.abstractmethod
    def get(self, condition: Optional[Dict] = None) -> List[Device]:
        pass


class DeviceJSONHandler(DeviceHandler):
    def __init__(self, location: str) -> None:
        """
        :param location: 文件的路径
        """
        if not os.path.exists(location):
            raise Exception("%s path has no exists" % location)
        self.path = location

    def add(self, data: List[Dict]) -> None:
        """
        :param data: List[Dict] 保存的数据
        """
        try:
            with open(self.path, "r+", encoding="utf-8") as f:
                _data = json.load(f)
                _data.extend(data)
            with open(self.path, "w+", encoding="utf-8") as f:
                json.dump(_data, f, ensure_ascii=False)
        except Exception as e:
            print("save device failed, error: %s" % str(e))

    def delete(self, condition: Dict) -> None:
        """
        :param condition: List[str] 删除的设备
        """
        try:
            with open(self.path, "r+", encoding="utf-8") as f:
                _data = json.load(f)
                _data: List[Dict]
            with open(self.path, "w+", encoding="utf-8") as f:
                result = []
                for idx, item in enumerate(_data):
                    flag = True
                    for k, v in condition.items():
                        if not v or item[k] != v:
                            flag = False
                    if not flag:
                        result.append(item)
                json.dump(result, f, ensure_ascii=False)
        except Exception as e:
            print("delete device failed, error: %s" % str(e))

    def update(self, data: Dict) -> None:
        """
        :param data: List[Dict] 更新的数据
        """
        pass

    def get(self, condition: Optional[Dict] = None) -> List[Device]:
        """
        :param condition: Dict[Str, Any] 筛选条件
        :return: List[Dict]
        """
        result = []
        try:
            with open(self.path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                if not condition:
                    return [Device.to_model(**item) for item in data]
                for item in data:
                    for k, v in condition.items():
                        if not v:
                            continue
                        if item[k] != v:
                            break
                    else:
                        result.append(Device.to_model(**item))
        except Exception as e:
            print("search device by condition failed, error: %s" % str(e))
        return result


class DeviceORMHandler(DeviceHandler):
    def __init__(self, db_handler: scoped_session):
        self.db_handler = db_handler

    def add(self, args: List[Dict]):
        if self.db_handler is None:
            raise Exception("has no active db handler")
        devices = []
        for item in args:
            device = Devices.to_model(**item)
            device.detail = DeviceDetail.to_model(**item)
            devices.append(device)
        self.db_handler.add_all(devices)
        self.db_handler.commit()

    def delete(self, args: List[int]):
        if self.db_handler is None:
            raise Exception("has no active db handler")
        Devices.query.filter(Devices.sn.in_(args)).delete()
        self.db_handler.commit()

    def update(self, args: List[Dict]):
        if self.db_handler is None:
            raise Exception("has no active db handler")
        for item in args:
            # {"sn": "", "vendor": "", "model": "", "detail": {"device_type": "", "channel": ""}}
            if "sn" not in item:
                continue
            sn = item.pop("sn")
            if "detail" in item:
                DeviceDetail.query.filter_by(sn=sn).update(item.pop("detail"))
            Devices.query.filter_by(sn=sn).update(item)
        self.db_handler.commit()

    def get(self, filters: Optional[Dict] = None) -> List[Device]:
        devices_model = Devices.query.filter_by(**(filters or {})).all()
        return [Device.from_model(item) for item in devices_model]

#
# if __name__ == '__main__':
#     device_db = DeviceDBHandler("root", "Yfy98333498", "localhost", "python_ops")
#     res = device_db.get({"model": "cisco_ios"})
#     print(res[0])
#     device_db.close_db()
