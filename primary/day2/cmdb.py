import json
import sys
import os
import time


class Store:
    version = None
    update_time = None

    def __init__(self, store_type, store_uri):
        self.store_type = store_type  # 存储介质类型
        self.store_uri = store_uri  # 存储介质的路径

    def save(self, data):  # 存储方法
        data["version"] = (Store.version or 1) + 1
        data["update_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(self.store_uri, "w+") as f:
            json.dump(data, f, indent=2)

    def read(self):  # 读取方法
        with open(self.store_uri, "r+") as f:
            data = json.load(f)
            try:
                Store.version = data.pop("version")
                Store.update_time = data.pop("update_time")
            except Exception:
                pass
        return data


class CMDB:
    version = None
    update_time = None

    def __init__(self, store):
        self.store = store
        self.operations = self.methods()

    def methods(self):
        ops = []
        for m in dir(self):
            if m.startswith("__") or m.endswith("__"):
                continue
            if not callable(getattr(self, m)):
                continue
            ops.append(m)
        return ops

    def execute(self, op, args):
        if op not in self.operations:
            raise Exception("%s is not valid CMDB operation, should is %s" % (op, ",".join(self.operations)))
        method = getattr(self, op)
        return method(*args)

    def init(self, region):
        data = self.store.read()
        if region in data:
            raise Exception("region %s already exists" % region)
        data[region] = {"idc": region, "switch": {}, "router": {}}
        self.store.save(data)
        return region

    def add(self, path, attrs):
        attrs = CMDB.check_parse(attrs)
        if attrs is None:
            raise Exception("attrs is invalid json string")
        data = self.store.read()
        target_path, last_seg = CMDB.locate_path(data, path)
        if last_seg in target_path:
            raise Exception("%s already exists in %s, please use update operation" % (last_seg, path))
        target_path[last_seg] = attrs
        self.store.save(data)
        return attrs

    def delete(self, path, attrs=None):
        attrs = CMDB.check_parse(attrs)
        data = self.store.read()
        target_path, last_seg = CMDB.locate_path(data, path)
        if attrs is None:
            if last_seg not in target_path:
                raise Exception("%s is not in data" % path)
            target_path.pop(last_seg)
        if isinstance(attrs, list):
            for attr in attrs:
                if attr not in target_path[last_seg]:
                    print("attr %s not in target_path" % attr)
                    continue
                if isinstance(target_path[last_seg], dict):
                    target_path[last_seg].pop(attr)
                if isinstance(target_path[last_seg], list):
                    target_path[last_seg].remove(attr)
        self.store.save(data)
        return attrs

    def update(self, path, attrs):
        attrs = CMDB.check_parse(attrs)
        if attrs is None:
            raise Exception("attrs is invalid json string")
        data = self.store.read()
        target_path, last_seg = CMDB.locate_path(data, path)
        if type(attrs) != type(target_path[last_seg]):
            raise Exception("update attributes and target_path attributes are different type.")
        if isinstance(attrs, dict):
            target_path[last_seg].update(attrs)
        elif isinstance(attrs, list):
            target_path[last_seg].extend(attrs)
            target_path[last_seg] = list(set(target_path[last_seg]))
        else:
            target_path[last_seg] = attrs
        self.store.save(data)
        return attrs

    def get(self, path):
        if "/" not in path:
            raise Exception("please input valid path")
        data = self.store.read()
        if path == "/":
            return json.dumps(data, indent=2)
        try:
            target_path, last_seg = CMDB.locate_path(data, path)
            ret = target_path[last_seg]
        except KeyError:
            raise Exception("path %s is invalid" % path)
        return json.dumps(ret, indent=2)

    @staticmethod
    def check_parse(attrs):
        if attrs is None:  # 判断attrs的合法性
            return None
        try:
            attrs = json.loads(attrs)
            return attrs
        except Exception:
            raise Exception("attributes is not valid json string")

    @staticmethod
    def locate_path(data, path):
        target_path = data
        path_seg = path.split("/")[1:]
        for seg in path_seg[:-1]:
            if seg not in target_path:
                print("location path is not exists in data, please use add function")
                return
            target_path = target_path[seg]
        return target_path, path_seg[-1]


class Params:
    def __init__(self, operations) -> None:
        self.operations = operations

    def parse(self, args):
        if len(args) < 3:
            raise Exception("please input operation and args, operations: %s" % ",".join(self.operations))
        operation = args[1]
        params = args[2:]
        return operation, params


if __name__ == "__main__":
    try:
        file_path = os.path.join(os.path.dirname(__file__), "data.json")
        file_store = Store("FILE", file_path)  # 实例化一个文件存储的存储对象
        cmdb = CMDB(file_store)  # 传入读出的数据源实例化一个CMDB的对象
        cmd_params = Params(cmdb.operations)  # 实例化从命令行获取参数的对象
        op, args = cmd_params.parse(sys.argv)  # 使用参数对象的解析方法解析出要做的操作和具体的参数
        result = cmdb.execute(op, args)  # 传入参数对象解析出的操作和具体参数，调用CMDB对象的执行操作方法
        print(result)
    except Exception as e:
        print(e)
