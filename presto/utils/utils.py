import functools


def output(*args):
    for arg in args:
        print arg


def input():
    return raw_input()


def need_providers(func, *args, **kwargs):
    @functools.wraps(func)
    def _func(*args, **kwargs):
        from presto.models import config
        if not config.providers:
            from presto.utils.exceptions import PrestoCfgException
            raise PrestoCfgException("Add providers please.")
        return func(*args, **kwargs)
    return _func
