import time
from functools import wraps


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

