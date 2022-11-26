import os
import json
import abc
from typing import List, Dict, Optional, Tuple
import pymysql
from pymysql.cursors import Cursor, DictCursor


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
        device = Device()
        for k, v in kwargs.items():
            if hasattr(device, k):
                setattr(device, k, v)
        if device.channel == "telnet":
            device.channel_port = 23
        return device

    def __str__(self):
        return json.dumps(self.__dict__)


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


class DeviceDBHandler(DeviceHandler):
    def __init__(self, user: str, password: str, host: str, database: str, port: int = 3306) -> None:
        self.conn = pymysql.connect(user=user, password=password, host=host, port=port, database=database, cursorclass=DictCursor)
        self.conn: pymysql.connections.Connection

    def get_conn(self) -> Cursor:
        if self.conn is None:
            raise Exception("mysql is lost connection")
        return self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def add(self, data: List[Dict]) -> None:
        cursor = self.get_conn()
        device_sql = "insert into devices (sn, ip, hostname, idc, vendor, model, role) values (%s, %s, %s, %s, %s, %s, %s);"
        device_detail_sql = "insert into device_detail values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        device_data = []
        device_detail_data = []
        for item in data:
            device_data.append([
                item.get("sn", ""), item.get("ip", ""), item.get("hostname", ""), item.get("idc", ""),
                item.get("vendor", ""), item.get("model", ""), item.get("role", "")
            ])
            device_detail_data.append([
                item.get("sn", ""), item.get("ipv6", ""), item.get("console_ip", ""), item.get("row", ""),
                item.get("column", ""), item.get("last_start", ""), item.get("runtime", ""), item.get("image_version", ""),
                item.get("over_warrant"), item.get("warrant_time")
            ])
        try:
            cursor.executemany(device_sql, device_data)
            cursor.executemany(device_detail_sql, device_detail_data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception("db insert failed, error: %s" % str(e))
        finally:
            cursor.close()

    def delete(self, data: Dict) -> None:
        pass

    def update(self, data: Dict) -> None:
        pass

    def get(self, condition: Optional[Dict] = None) -> List[Device]:
        cursor = self.get_conn()
        sql = "select ip, hostname, vendor, model, hardware, channel, device_type from devices " \
              "join device_detail on devices.sn = device_detail.sn"
        where_str = []
        if condition is not None:
            for k, v in condition.items():
                if isinstance(v, int):
                    where_str.append("%s=%d" % (k, v))
                else:
                    where_str.append("%s='%s'" % (k, v))
        if len(where_str) > 0:
            sql += (" where %s" % ",".join(where_str))
        cursor.execute(sql)
        result = cursor.fetchall()
        return [Device().to_model(**item) for item in result]


if __name__ == '__main__':
    device_db = DeviceDBHandler("root", "Yfy98333498", "localhost", "python_ops")
    res = device_db.get({"model": "cisco_ios"})
    print(res[0])
    device_db.close_db()
