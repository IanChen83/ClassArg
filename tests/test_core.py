from types import SimpleNamespace

import pytest

import classarg.core as core
from classarg._typing import Tuple


'''
please check out
https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios
'''


def _gen_getfullargspec_testcase():
    def func(a, b=1, *c, d: int, e=2, **f): pass

    class X:
        def __init__(self, a, b=1, *c, d: int, e=2, **f): pass

        def __call__(self, a, b=1, *c, d: int, e=2, **f): pass

        def func(self, a, b=1, *c, d: int, e=2, **f): pass

        @classmethod
        def func2(cls, a, b=1, *c, d: int, e=2, **f): pass

        @staticmethod
        def func3(a, b=1, *c, d: int, e=2, **f): pass

    def func2(a, b=(1, 2)): pass

    class Y:
        pass

    null_expect = SimpleNamespace(
        args=[], varargs=None, varkw=None, defaults=tuple(),
        kwonlyargs=tuple(), kwonlydefaults={}, annotations={},
        docstring=None, aliases=dict())

    expect = SimpleNamespace(
        args=['a', 'b'], varargs='c', varkw='f', defaults=(1,),
        kwonlyargs=['d', 'e'], kwonlydefaults={'e': 2},
        annotations={'b': int, 'd': int, 'e': int},
        docstring=None, aliases=dict())

    expect_with_self = SimpleNamespace(
        args=['self', 'a', 'b'], varargs='c', varkw='f', defaults=(1,),
        kwonlyargs=['d', 'e'], kwonlydefaults={'e': 2},
        annotations={'b': int, 'd': int, 'e': int},
        docstring=None, aliases=dict())

    expect2 = SimpleNamespace(
        args=['a', 'b'], varargs=None, varkw=None, defaults=((1, 2), ),
        kwonlyargs=tuple(), kwonlydefaults={},
        annotations={'b': Tuple[int, int]},
        docstring=None, aliases=dict())

    yield func, expect                  # func-expect0 function
    yield X.func, expect_with_self      # func-expect1 class method
    yield X(1, d=2).func, expect        # func-expect2 instance method
    yield X(1, d=2).func2, expect       # func-expect3 instance classmethod
    yield X(1, d=2).func3, expect       # func-expect4 instance staticmethod
    yield X, expect                     # func-expect5 class, __init__ defined
    yield Y, null_expect                # func-expect6 class
    yield X(1, d=2), expect             # func-expect7 class instance __call__
    yield func2, expect2                # func-expect8 secial typing function

    yield Y(), TypeError()              # func-expect9 error
    yield 'error input', TypeError()    # func-expect10 error


@pytest.mark.parametrize('func, expect', list(_gen_getfullargspec_testcase()))
def test_getfullargspec(func, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = core.getfullargspec(func)
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)

    else:
        assert core.parse(func) == expect


def _gen_parse_argv_testcase():
    yield '中文', '中文'
    yield '--', '--'
    yield '-f', {'f': True}
    yield '--no-error', {'no-error': True}
    yield '--verbose', {'verbose': True}
    yield '-x=1', {'x': '1'}
    yield '--retry=2', {'retry': '2'}
    yield '--no_error', {'no_error': True}
    yield '--retry_times=2', {'retry_times': '2'}
    yield '--help=中文', {'help': '中文'}
    yield '--中文=中文', {'中文': '中文'}
    yield '--x2=2', {'x2': '2'}
    yield '--2d=2', core.ArgumentError()


@pytest.mark.parametrize('args, expect', list(_gen_parse_argv_testcase()))
def test_parse_argv(args, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = core._parse_one_arg(args)
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)

    else:
        assert core._parse_one_arg(args) == expect
