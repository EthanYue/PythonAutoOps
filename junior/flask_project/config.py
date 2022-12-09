class Config:
    DEBUG = False
    LOG_LEVEL = "INFO"
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    # 查询时会显示原始SQL语句
    SQLALCHEMY_ECHO = True
    # 数据库连接格式
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Yfy98333498@localhost:3306/python_ops?charset=utf8"
    # 动态追踪修改设置，如未设置只会提示警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 数据库连接池的大小
    SQLALCHEMY_POOL_SIZE = 10
    # 指定数据库连接池的超时时间
    SQLALCHEMY_POOL_TIMEOUT = 10
    # 控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃。
    SQLALCHEMY_MAX_OVERFLOW = 2


class ProductionConfig(Config):
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:YfyH98333498.@localhost:3306/python_ops?charset=utf8"
    pass


config_mapper = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
}
