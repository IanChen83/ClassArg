import pytest
from classarg._typing import Union, Optional, List, Set, normalize_type


NoneType = type(None)
_builtin = set((int, float, bool, str, NoneType))


def _gen_types_testcase():
    # Correct cases
    yield Union, int, int
    yield Union, None, NoneType
    yield Union, (int, str), ('typing.Union', (int, str))
    yield Optional, None, NoneType
    yield Optional, int, ('typing.Union', (int, NoneType))
    yield List, int, ('typing.List', (int, ))
    yield Set, int, ('typing.Set', (int, ))

    # Failed cases
    yield Union, tuple(), TypeError()
    yield Optional, (int, str), TypeError()
    yield List, (int, str), TypeError()


@pytest.mark.parametrize('type1, type2, expect', list(_gen_types_testcase()))
def test_parse_metaclass(type1, type2, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = type1[type2]
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)

    else:
        res = normalize_type(type1[type2])
        if expect in _builtin:
            assert res is expect

        else:
            type_name, types = expect

            assert (str(res.__origin__), res.__args__) == (type_name, types)


def _gen_type_str_testcase():
    yield 'Union[int]', int
    yield 'typing.Union[int]', int
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
            ret = normalize_type(type_str)
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)

    else:
        if expect in _builtin:
            assert normalize_type(type_str) is expect

        else:
            res = normalize_type(type_str)
            type_name, types = expect

            assert (str(res.__origin__), res.__args__) == (type_name, types)
