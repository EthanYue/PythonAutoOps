import json
import sys


def read_file():
    with open("data.json", "r+") as f:
        data = json.load(f)
    return data


def write_file(data):
    with open("data.json", "w+") as f:
        json.dump(data, f, indent=2)


def check_parse(attrs):
    if attrs is None:  # 判断attrs的合法性
        print("attributes is None")
        return
    try:
        attrs = json.loads(attrs)
        return attrs
    except Exception:
        print("attributes is not valid json string")
        return


def locate_path(data, path):
    target_path = data
    path_seg = path.split("/")[1:]
    for seg in path_seg[:-1]:
        if seg not in target_path:
            print("update path is not exists in data, please use add function")
            return
        target_path = target_path[seg]
    return target_path, path_seg[-1]


def init(region):
    with open("data.json", "r+") as f:
        data = json.load(f)
    if region in data:
        print("region %s already exists" % region)
        return
    data[region] = {"idc": region, "switch": {}, "router": {}}
    with open("data.json", "w+") as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))


def add(path, attrs=None):
    attrs = check_parse(attrs)
    if not attrs:
        return
    with open("data.json", "r+") as f:
        data = json.load(f)
    target_path, last_seg = locate_path(data, path)
    if last_seg in target_path:
        print("%s already exists in %s, please use update operation" % (last_seg, path))
        return
    target_path[last_seg] = attrs
    with open("data.json", "w+") as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))


def update(path, attrs):
    attrs = check_parse(attrs)
    if not attrs:
        return
    data = read_file()
    target_path, last_seg = locate_path(data, path)
    if isinstance(type(attrs), type(target_path[last_seg])):
        print("update attributes and target_path attributes are different type.")
        return
    if isinstance(attrs, dict):
        target_path[last_seg].update(attrs)
    elif isinstance(attrs, list):
        target_path[last_seg].extend(attrs)
        target_path[last_seg] = list(set(target_path[last_seg]))
    else:
        target_path[last_seg] = attrs
    write_file(data)
    print(json.dumps(data, indent=2))


def delete(path, attrs=None):
    attrs = check_parse(attrs)
    data = read_file()
    target_path, last_seg = locate_path(data, path)
    if not attrs:
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
    write_file(data)
    print(json.dumps(data, indent=2))


def get(path):
    data = read_file()
    target_path, last_seg = locate_path(data, path)
    print(json.dumps(target_path[last_seg], indent=2))


if __name__ == "__main__":
    operations = ["get", "update", "delete"]
    args = sys.argv
    if len(args) < 3:
        print("please input operation and args")
    else:
        if args[1] == "init":
            init(args[2])
        elif args[1] == "add":
            add(*args[2:])
        elif args[1] == "get":
            get(args[2])
        elif args[1] == "update":
            update(*args[2:])
        elif args[1] == "delete":
            delete(*args[2:])
        else:
            print("operation must be one of get,update,delete")
