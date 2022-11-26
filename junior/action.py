import json
import abc
from typing import List, Dict, Optional


class CommandType:
    Show = "show"
    Config = "config"


class Action:
    name = ""
    description = ""
    vendor = ""
    model = ""
    cmd = ""
    type = ""
    parse_type = ""
    parse_content = ""

    @classmethod
    def to_model(cls, **kwargs):
        action = Action()
        for k, v in kwargs.items():
            if hasattr(action, k):
                setattr(action, k, v)
        return action

    def __str__(self):
        return json.dumps(self.__dict__)


class ActionHandler(abc.ABC):
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
    def get(self, condition: Optional[Dict] = None) -> List[Action]:
        pass


class ActionJSONHandler(ActionHandler):
    def __init__(self, location: str) -> None:
        """
        :param location: 文件的路径
        """
        import os
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
            print("save action failed, error: %s" % str(e))

    def delete(self, condition: Dict) -> None:
        """
        :param condition: List[str] 删除的命令
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
                            break
                    if not flag:
                        result.append(item)
                json.dump(result, f, ensure_ascii=False)
        except Exception as e:
            print("delete action failed, error: %s" % str(e))

    def update(self, data: Dict) -> None:
        """
        :param data: List[Dict] 更新的数据
        """
        pass

    def get(self, condition: Optional[Dict] = None) -> List[Action]:
        """
        :param condition: Dict[Str, Any] 筛选条件
        :return: List[Dict]
        """
        result = []
        try:
            with open(self.path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                if not condition:
                    return [Action.to_model(**item) for item in data]
                for item in data:
                    for k, v in condition.items():
                        if not v:
                            continue
                        if item[k] != v:
                            break
                    else:
                        result.append(Action.to_model(**item))
        except Exception as e:
            print("search action by condition failed, error: %s" % str(e))
        return result


class ActionDBHandler(ActionHandler):
    pass


if __name__ == '__main__':
    action_json = ActionJSONHandler("action.json")
    res = action_json.get({"vendor": "cisco", "model": "nexus"})  # get by conditions
    action_json.add([{ "name": "fans_check", "description": "风扇检查", "vendor": "huawei", "model": "", "cmd": "display fans", "type": "show", "parse_type": "regexp", "parse_content": "" }])
    action_json.delete({"cmd": "display fans", "vendor": "h3c"})
    res = action_json.get()

