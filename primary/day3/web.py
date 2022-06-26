import socket


def make_server(ip, port, app):
    # 处理套接字通信
    sock = socket.socket()
    sock.bind((ip, port))
    sock.listen(5)
    print('Starting development server at http://%s:%s/' %(ip,port))
    conn = None
    try:
        while True:
            conn, addr = sock.accept()
            # 1、接收浏览器发来的请求信息
            recv_data = conn.recv(1024)
            # 2、将请求信息直接转交给application处理，得到返回值
            res = app(recv_data)
            # 3、向浏览器返回消息（此处并没有按照http协议返回）
            conn.send(res)
            conn.close()
    except Exception:
        pass
    finally:
        conn.close()


def app(environ):  # 代表application
    # 处理业务逻辑
    print(b"hello world")
    return b"hello world"


if __name__ == '__main__':
    make_server('127.0.0.1', 8080, app)
