from sqlalchemy import text, DateTime, Numeric
from utils import to_model as tm
from . import db


class Devices(db.Model):
    __tablename__ = "devices"
    sn = db.Column(db.String(128), primary_key=True, comment="资产号")
    ip = db.Column(db.String(16), nullable=False, comment="IP地址")
    hostname = db.Column(db.String(128), nullable=False, comment="主机名")
    idc = db.Column(db.String(32), comment="机房")
    vendor = db.Column(db.String(16), comment="厂商")
    model = db.Column(db.String(16), comment="型号")
    role = db.Column(db.String(8), comment="角色")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")

    detail = db.relationship("DeviceDetail", uselist=False, backref="device")
    ports = db.relationship("Ports", uselist=True, backref="device")

    @classmethod
    def to_model(cls, **kwargs):
        return tm(cls, **kwargs)

    def to_dict(self):
        res = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(col.type, DateTime):  # 判断类型是否为DateTime
                if not val:  # 判断实例中该字段是否有值
                    value = ""
                else:  # 进行格式转换
                    value = val.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(col.type, Numeric):  # 判断类型是否为Numeric
                value = float(val)  # 进行格式转换
            else:  # 剩余的直接取值
                value = val
            res[col.name] = value
        return res


class DeviceDetail(db.Model):
    __tablename = "device_detail"
    sn = db.Column(db.String(128), db.ForeignKey(Devices.sn, ondelete="cascade"), primary_key=True, comment="资产号")
    ipv6 = db.Column(db.String(16), nullable=False, comment="IPv6地址")
    console_ip = db.Column(db.String(16), nullable=False, comment="console地址")
    row = db.Column(db.String(8), comment="机柜行")
    column = db.Column(db.String(8), comment="机柜列")
    last_start = db.Column(db.DateTime(), comment="最近启动时间")
    runtime = db.Column(db.Integer, comment="运行时长")
    image_version = db.Column(db.String(128), comment="镜像版本")
    over_warrant = db.Column(db.BOOLEAN, comment="是否过保")
    warrant_time = db.Column(db.DateTime(), comment="过保时间")
    device_type = db.Column(db.String(32), comment="远程连接设备类型")
    channel = db.Column(db.String(8), comment="远程连接方式[ssh|telnet]")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")

    @classmethod
    def to_model(cls, **kwargs):
        return tm(cls, **kwargs)

    def to_dict(self):
        res = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(col.type, DateTime):  # 判断类型是否为DateTime
                if not val:  # 判断实例中该字段是否有值
                    value = ""
                else:  # 进行格式转换
                    value = val.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(col.type, Numeric):  # 判断类型是否为Numeric
                value = float(val)  # 进行格式转换
            else:  # 剩余的直接取值
                value = val
            res[col.name] = value
        return res


class Ports(db.Model):
    __tablename = "ports"
    sn = db.Column(db.String(128), db.ForeignKey(Devices.sn), primary_key=True, comment="资产号")
    port_id = db.Column(db.String(16), nullable=False, primary_key=True, comment="端口ID")
    port_name = db.Column(db.String(64), nullable=False, comment="端口名称")
    port_type = db.Column(db.String(16), comment="端口类型")
    bandwidth = db.Column(db.Integer, comment="端口速率")
    link_status = db.Column(db.String(8), comment="链路状态")
    admin_status = db.Column(db.String(8), comment="管理状态")
    interface_ip = db.Column(db.String(16), comment="端口IP")
    vlan_id = db.Column(db.String(8), comment="端口所属VLAN")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")

    @classmethod
    def to_model(cls, **kwargs):
        return tm(cls, **kwargs)

    def to_dict(self):
        res = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(col.type, DateTime):  # 判断类型是否为DateTime
                if not val:  # 判断实例中该字段是否有值
                    value = ""
                else:  # 进行格式转换
                    value = val.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(col.type, Numeric):  # 判断类型是否为Numeric
                value = float(val)  # 进行格式转换
            else:  # 剩余的直接取值
                value = val
            res[col.name] = value
        return res

