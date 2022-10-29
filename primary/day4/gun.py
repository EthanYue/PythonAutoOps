import multiprocessing
import gevent.monkey
gevent.monkey.patch_all()

bind = '0.0.0.0:8080'  # 绑定的ip以及端口号
chdir = '/home/flaskProject'  # gunicorn要切换到的目的工作目录
timeout = 60  # 超时
worker_class = 'gevent'  # 使用gevent模式，还可以使用sync 模式，默认的是sync模式
workers = multiprocessing.cpu_count() * 2 + 1  # 启动的进程数
loglevel = "info"  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'  # 设置gunicorn访问日志格式，错误日志无法设置
pidfile = "gunicorn.pid"
accesslog = "access.log"
errorlog = "error.log"
daemon = True  # 是否后台运行