import pytest
from classarg._typing import Union, Optional


NoneType = type(None)


def _gen_types_testcase():
    yield Union, int, int
    yield Union, None, NoneType
    yield Optional, int, ('typing.Union', (int, NoneType))


_builtin = set((int, float, bool, str, type(None)))


@pytest.mark.parametrize('type1, type2, expect', list(_gen_types_testcase()))
def test_parse(type1, type2, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = type1[type2]
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)

    else:
        if expect in _builtin:
            assert type1[type2] is expect

        else:
            res = type1[type2]
            type_name, types = expect

            assert str(res.__origin__) == type_name
            assert set(res.__args__) == set(types)
