import sys
from types import SimpleNamespace
from inspect import getfullargspec, isfunction, ismethod, isclass

from ._typing import get_type_hints, Union, Optional


__all__ = (
    'match',
    'run',
    'parse',
    'parse_annotation',
    'validate',
)


def validate(func, kwargs):
    if not hasattr(func, '_classarg_val'):
        return

    for validate_func in func._classarg_val:
        validate_func(func=func, match=kwargs)


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
def parse_annotation(func):
    annotations = get_type_hints(func)
    return annotations


def _get_normalized_spec(func, skip_annotation=False):
    spec = getfullargspec(func)
    ret = {
        'args': tuple(),
        'varargs': None,
        'varkw': None,
        'defaults': tuple(),
        'kwonlyargs': tuple(),
        'kwonlydefaults': dict(),
    }

    for key in ret:
        value = getattr(spec, key)
        if value:
            ret[key] = value

    if skip_annotation:
        ret['annotations'] = dict()
    else:
        ret['annotations'] = parse_annotation(func)

    return SimpleNamespace(**ret)


def parse(func, *, skip_annotation=False):
    if isfunction(func):
        spec = _get_normalized_spec(func, skip_annotation)

    elif ismethod(func):
        spec = _get_normalized_spec(func, skip_annotation)
        del spec.args[0]

    elif isclass(func):
        spec = _get_normalized_spec(func.__init__, skip_annotation)
        del spec.args[0]

        if func.__init__ is object.__init__:
            spec.varargs = None
            spec.varkw = None

    elif hasattr(func, '__call__'):
        spec = _get_normalized_spec(func.__call__, skip_annotation)
        del spec.args[0]

    else:
        raise TypeError('Could not determine the signature of ' + str(func))

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
