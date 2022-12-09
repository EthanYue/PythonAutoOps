from typing import Dict, Any


def to_model(cls: Any, **kwargs: Dict) -> Any:
    """
    根据关键字参数生成对象
    :param cls: ClassVar 目标对象
    :param kwargs: Dict 关键字字典
    :return: ClassVar
    """
    device = cls()  # 实例化一个对象
    columns = [c.name for c in cls.__table__.columns]  # 获取模型定义的所有列属性的名字
    for k, v in kwargs.items():  # 遍历传入kwargs的键值
        if k in columns:  # 如果键包含在列名中，则为该对象赋加对应的属性值
            setattr(device, k, v)
    return device


def to_dict(self: Any) -> Dict:
    """
    将实例对象的属性生成字典
    :param self: ClassVar 对象实例
    :return: Dict
    """
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}