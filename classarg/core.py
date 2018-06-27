import re
import sys
from types import SimpleNamespace
from inspect import getfullargspec, isfunction, ismethod, isclass


__all__ = (
    'match',
    'run',
    'parse',
    'validate',
    'ArgumentError',
)


class ArgumentError(Exception):
    pass


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
        from ._typing import load_type_hints  # load module on demand
        load_type_hints(spec)

    return spec


pattern = re.compile(r'^-{1,2}([^=\s]+)(?==?(\S*))')
def _parse_one_arg(arg): # noqa
    if arg == '--':
        return arg

    matched = pattern.search(arg)
    if matched is None:
        return arg

    key, value = matched.groups()
    value = True if value == '' else value
    return {key: value}


def _match_args(spec, args):
    ret = []
    for arg in args:
        arg = _parse_one_arg(arg)

        if ret and isinstance(ret[-1], dict) and ret[-1]:
            pass

    return ret


def match(func, *, args=None, **options):
    args = args if args is not None else sys.argv[1:]
    if isinstance(func, SimpleNamespace):
        spec = func
    else:
        skip_type_hints = options.get('skip_type_hints', False)
        spec = parse(func, skip_type_hints)

    _match_args(spec, args)

    return dict()


def run(func, *, args=None, **options):
    skip_type_hints = options.get('skip_type_hints')

    spec = parse(func,
                 args=args,
                 skip_type_hints=skip_type_hints)
    matcher = match(spec,
                    args=args,
                    skip_type_hints=skip_type_hints)
    validate(func, matcher)

    return func()
