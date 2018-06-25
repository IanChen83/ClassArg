import pytest
from classarg._typing import _type_transform


NoneType = type(None)
_builtin = set((int, float, bool, str, NoneType))


def _gen_type_str_testcase():
    yield 'Union[int]', int
    yield 'Union[None]', NoneType
    yield 'Union[Union[None]]', NoneType
    yield 'Union[int, str]', ('typing.Union', (int, str))
    yield 'Optional[None]', NoneType
    yield 'Optional[int]', ('typing.Union', (int, NoneType))
    yield 'List[int]', ('typing.List', (int, ))
    yield 'Set[int]', ('typing.Set', (int, ))


@pytest.mark.parametrize('type_str, expect', list(_gen_type_str_testcase()))
def test_parse_type_str(type_str, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = _type_transform(type_str)
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)

    else:
        if expect in _builtin:
            assert _type_transform(type_str) is expect

        else:
            res = _type_transform(type_str)
            type_name, types = expect

            assert (str(res.__origin__), res.__args__) == (type_name, types)
