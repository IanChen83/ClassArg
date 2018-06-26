import pytest

import classarg.core as core
import classarg.validation_funcs as v_funcs


def _gen_at_least_testcase():
    def func(a, b=True, c=False, d=3, *e, f: bool, g: str): pass
    spec = core.parse(func)

    matcher = dict(a=True, b=True, c=False, d=3, f=True, g='g')

    # 0. should always passed
    yield ('a', 'b'), spec, matcher, None

    # 1. should always failed
    yield ('c', ), spec, matcher, ValueError()

    # 2. when flags not found in spec
    yield ('a', 'z'), spec, matcher, KeyError()

    # 3. when flag annotation not the right type
    yield ('a', 'g'), spec, matcher, TypeError()

    # 4. when default value not the right type
    yield ('a', 'd'), spec, matcher, TypeError()


@pytest.mark.parametrize('flags, spec, matcher, expect',
                         list(_gen_at_least_testcase()))
def test_parse(flags, spec, matcher, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            v_funcs.at_least(*flags, spec=spec, matcher=matcher)
        if not isinstance(expect, e_info.type):
            raise e_info.value

    else:
        assert v_funcs.at_least(*flags, spec=spec, matcher=matcher) == expect
