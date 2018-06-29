import pytest
from classarg._typing import (
    Union, Optional, List, Set, Tuple,
    normalize_type, infer_default_type,
)


NoneType = type(None)
_builtin = set((int, float, bool, str, NoneType))


def _gen_types_testcase():
    # Correct cases
    yield Union, int, int
    yield Union, None, NoneType
    yield Union, (int, str), ('typing.Union', (int, str))
    yield Union, (int, str, int), ('typing.Union', (int, str))
    yield Optional, None, NoneType
    yield Optional, int, ('typing.Union', (int, NoneType))
    yield List, int, ('typing.List', (int, ))
    yield Set, int, ('typing.Set', (int, ))
    yield Tuple, (int, str), ('typing.Tuple', (int, str))

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
    yield 'Union[None]', NoneType
    yield 'Union[Union[None]]', NoneType
    yield 'Union[Union[int, str], str]', ('typing.Union', (int, str))
    yield 'Union[int, str]', ('typing.Union', (int, str))
    yield 'Union[int, str, int]', ('typing.Union', (int, str))
    yield 'Optional[None]', NoneType
    yield 'Optional[int]', ('typing.Union', (int, NoneType))
    yield 'List[int]', ('typing.List', (int, ))
    yield 'Set[int]', ('typing.Set', (int, ))
    yield 'Tuple[int]', ('typing.Tuple', (int, ))
    yield 'Tuple[]', TypeError()
    yield 'Tuple', TypeError()


@pytest.mark.parametrize('type_str, expect', list(_gen_type_str_testcase()))
def test_eval_type_from_str(type_str, expect):
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


def _gen_default_testcase():
    yield 3, int
    yield 3.0, float
    yield True, bool
    yield 'asdf', str
    yield None, None
    yield NoneType, None
    yield (5, 3), Tuple[int, int]


@pytest.mark.parametrize('default, expect', list(_gen_default_testcase()))
def test_infer_default_type(default, expect):
    assert infer_default_type(default) == expect
