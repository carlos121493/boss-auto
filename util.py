import time
import os
from functools import wraps
from tenacity import retry, stop_after_attempt
from adbutils.errors import AdbError
import uiautomator2 as u2

def decTime(fn):
    @wraps(fn)
    def innerFn(*args, **kwargs):
        start = time.time()
        name = fn.__name__
        temp = fn(*args, **kwargs)
        end = time.time()
        print('{0} 耗时 {1}'.format(name, end - start))
        return temp
    return innerFn

@retry(stop=stop_after_attempt(2))
def connect():
    try:
        d = u2.connect('127.0.0.1:7555')
        return d
    except AdbError:
        os.popen('adb connect 127.0.0.1:7555')
        print('链接失败，尝试重连中...')
        print(AdbError)
        raise AdbError


class LazyProperty(object):
    """
    LazyProperty
    explain: http://www.spiderpy.cn/blog/5/
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


class CachedCalled:
    """
    """
    cache = {}

    def __call__(self, func):
        @wraps(func)
        def innerFn(*args, **kwargs):
            key = func.__name__
            keys = self.cache.keys()
            if key in keys:
                return self.cache[key]
            value = func(*args, **kwargs)
            self.cache[key] = value
            return value
        return innerFn

