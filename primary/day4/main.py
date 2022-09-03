from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Devices(db.Model):
    """
    CREATE TABLE IF NOT EXISTS `devices` (
        `id` INT AUTO_INCREMENT COMMENT '自增主键',
        `ip` VARCHAR(16) NOT NULL COMMENT 'IP地址',
        `hostname` VARCHAR(128) COMMENT '主机名',
        `idc` VARCHAR(32) COMMENT '机房',
        `row` VARCHAR(8) COMMENT '机柜行',
        `column` VARCHAR(8) COMMENT '机柜列',
        `vendor` VARCHAR(16) COMMENT '厂商',
        `model` VARCHAR(16) COMMENT '型号',
        `role` VARCHAR(8) COMMENT '角色',
        `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    """
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    ip = db.Column(db.String(16), nullable=False, comment="IP地址")
    hostname = db.Column(db.String(128), nullable=False, comment="主机名")
    idc = db.Column(db.String(32), comment="机房")
    row = db.Column(db.String(8), comment="机柜行")
    column = db.Column(db.String(8), comment="机柜列")
    vendor = db.Column(db.String(16), comment="厂商")
    model = db.Column(db.String(16), comment="型号")
    role = db.Column(db.String(8), comment="角色")
    created_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), comment="创建时间")
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=text('NOW()'), server_onupdate=text('NOW()'), comment="修改时间")


if __name__ == '__main__':
    # 增
    device1 = Devices(ip="10.0.0.4", hostname="BJ-R01-C01-N9K-00-00-01", idc="Beijing", row="R01", column="C01",
                      vendor="Cisco", model="Nexus9000", role="CSW")
    device2 = Devices(ip="10.0.0.5", hostname="BJ-R01-C01-N9K-00-00-02", idc="Beijing", row="R01", column="C02",
                      vendor="Cisco", model="Nexus9000", role="CSW")
    device3 = Devices(ip="10.0.0.6", hostname="BJ-R01-C01-N9K-00-00-03", idc="Beijing", row="R01", column="C03",
                      vendor="Cisco", model="Nexus9000", role="CSW")
    db.session.add_all([device1, device2, device3])
    db.session.commit()
    db.session.close()
