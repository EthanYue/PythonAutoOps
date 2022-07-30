import time
from functools import wraps


# def timer(func):
#     def inner(num):
#         start = time.time()
#         func(num)
#         end = time.time()
#         print("%s cost %f seconds" % (func.__name__, end - start))
#
#     return inner


def timer1(func):
    @wraps(func)
    def inner(*args, **kwargs):
        """doc of inner"""
        start = time.time()
        ret = func(*args, **kwargs)
        end = time.time()
        print("%s cost %f seconds" % (func.__name__, end - start))
        return ret
    return inner


def timer(timeout=10):
    def func_log(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """doc of inner"""
            start = time.time()
            ret = func(*args, **kwargs)
            end = time.time()
            print("%s cost %f seconds" % (func.__name__, end - start))
            if end-start > timeout:
                raise Exception("%s run timeout" % func.__name__)
            return ret
        return wrapper
    return func_log


@timer(5)
def foo(num1, num2):
    """
    :param num1:
    :param num2:
    :return:
    """
    time.sleep(num1)
    return num2


if __name__ == "__main__":
    foo(3, 4)
