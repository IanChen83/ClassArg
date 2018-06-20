from inspect import FullArgSpec

import pytest
import classarg.core as core


'''
please check out
https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios
'''


def _gen_parse_testcase():
    def func(a, b=1, *c, d: int, e=2, **f): pass

    class X:
        def __init__(self, a, b=1, *c, d: int, e=2, **f): pass

        def __call__(self, a, b=1, *c, d: int, e=2, **f): pass

        def func(self, a, b=1, *c, d: int, e=2, **f): pass

        @classmethod
        def func2(cls, a, b=1, *c, d: int, e=2, **f): pass

        @staticmethod
        def func3(a, b=1, *c, d: int, e=2, **f): pass

    def func2(self, a, b=1, *c, d: int, e=2, **f): pass

    class Y:
        pass

    expect = FullArgSpec(
        args=['a', 'b'], varargs='c', varkw='f', defaults=(1,),
        kwonlyargs=['d', 'e'], kwonlydefaults={'e': 2}, annotations={'d': int})

    expect_with_self = FullArgSpec(
        args=['self', 'a', 'b'], varargs='c', varkw='f', defaults=(1,),
        kwonlyargs=['d', 'e'], kwonlydefaults={'e': 2}, annotations={'d': int})

    yield func, expect                  # func-expect0 function
    yield X(1, d=2).func, expect        # func-expect1 class method
    yield X.func, expect_with_self      # func-expect2 class instance method
    yield X.func2, expect               # func-expect3 class classmethod
    yield X.func3, expect               # func-expect4 class staticmethod
    yield X, NotImplementedError()      # func-expect5 class, __init__ defined
    yield Y, NotImplementedError()      # func-expect6 class
    yield X(1, d=2), expect             # func-expect7 class instance __call__
    yield Y(), TypeError()              # func-expect8 error
    yield 'error input', TypeError()    # func-expect9 error


@pytest.mark.parametrize('func, expect', list(_gen_parse_testcase()))
def test_parse(func, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            core.parse(func)
        assert isinstance(expect, e_info.type)

    else:
        assert core.parse(func) == expect
