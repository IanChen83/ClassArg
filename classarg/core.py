import sys
from types import SimpleNamespace
from inspect import getfullargspec, isfunction, ismethod, isclass

from ._typing import get_type_hints


__all__ = (
    'match',
    'run',
    'parse',
    'validate',
)


def validate(func, kwargs):
    if not hasattr(func, '_classarg_val'):
        return

    for validate_func in func._classarg_val:
        validate_func(func=func, match=kwargs)


def _get_normalized_spec(func):
    spec = getfullargspec(func)
    ret = {
        'args': tuple(),
        'varargs': None,
        'varkw': None,
        'defaults': tuple(),
        'kwonlyargs': tuple(),
        'kwonlydefaults': dict(),
        'annotations': dict(),
    }

    for key in ret:
        value = getattr(spec, key)
        if value:
            ret[key] = value

    return SimpleNamespace(**ret)


# We follow this cheat sheet
# http://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html#built-in-types
# but only support the following types
#
# 1. built-in types:
#    int, float, bool, str
#
# 2. collections:
#    List, Tuple, Set
#
# 3. misc:
#    Union, Optional
def parse(func, *, skip_type_hints=False):
    if isfunction(func):
        spec = _get_normalized_spec(func)

    elif ismethod(func):
        spec = _get_normalized_spec(func)
        del spec.args[0]

    elif isclass(func):
        spec = _get_normalized_spec(func.__init__)
        del spec.args[0]

        if func.__init__ is object.__init__:
            spec.varargs = None
            spec.varkw = None

    elif hasattr(func, '__call__'):
        spec = _get_normalized_spec(func.__call__)
        del spec.args[0]

    else:
        raise TypeError('Could not determine the signature of ' + str(func))

    if skip_type_hints:
        spec.annotations = {}
    else:
        spec.annotations = get_type_hints(spec)

    return spec


def match(func, args=None):
    if isinstance(func, SimpleNamespace):
        spec = func
    else:
        spec = parse(func)
    args = args or sys.argv[1:]

    # TODO: match spec and arguments

    return dict()


def run(func, args=None):
    spec = parse(func)
    matcher = match(spec, args)
    validate(func, matcher)

    return func()
