import re
import sys
from types import SimpleNamespace
from inspect import (
    getfullargspec as _getfullargspec,
    isfunction,
    ismethod,
    isclass,
)

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


_candidate_headers = (
    'args',
    'arguments',
    'keyword args',
    'keyword arguments',
    'parameters',
)
def _load_doc_hints(spec, docstring):  # noqa
    from .doc import parse_docstring
    descriptions, sections = parse_docstring(docstring)


def _load_type_hints(spec):
    from ._typing import parse_annotations, Optional, infer_default_type
    type_hints = parse_annotations(spec.annotations)

    defaults = dict(spec.kwonlydefaults)
    if spec.defaults:
        defaults.update({k: v for k, v in zip(reversed(spec.args),
                                              reversed(spec.defaults))})

    for key, value in defaults.items():
        if key in type_hints and value is None:
            type_hints[key] = Optional[type_hints[key]]

        elif key not in type_hints:
            try:
                type_hints[key] = infer_default_type(value)
            except TypeError:
                pass

    spec.annotations = type_hints


def _get_normalized_spec(func):
    if isfunction(func):
        spec = getfullargspec(func)

    elif ismethod(func):
        spec = getfullargspec(func)
        del spec.args[0]

    elif isclass(func):
        spec = getfullargspec(func.__init__)
        del spec.args[0]

        if func.__init__ is object.__init__:
            spec.varargs = None
            spec.varkw = None

    elif hasattr(func, '__call__'):
        spec = getfullargspec(func.__call__)
        del spec.args[0]

    else:
        raise TypeError('Could not determine the signature of ' + str(func))

    return spec


def getfullargspec(func):
    spec = _getfullargspec(func)
    ret = {
        'args': tuple(),
        'varargs': None,
        'varkw': None,
        'defaults': tuple(),
        'kwonlyargs': tuple(),
        'kwonlydefaults': dict(),
        'annotations': dict(),
        'docs': SimpleNamespace(),
    }

    for key in ret:
        if hasattr(spec, key):
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
def parse(func, **options):
    spec = _get_normalized_spec(func)
    skip_type_hints = options.get('skip_type_hints', False)
    skip_doc_hints = options.get('skip_doc_hints', False)

    if not skip_type_hints:
        _load_type_hints(spec)

    if (not skip_doc_hints and
            hasattr(func, '__doc__') and
            func.__doc__):
        _load_doc_hints(spec, func.__doc__)

    return spec


pattern = re.compile(r'^-{1,2}([^\d\W][\w-]*)(?==?(\S*))')
def _parse_one_arg(arg): # noqa
    if arg == '--':
        return arg

    matched = pattern.search(arg)
    if matched is None:
        if not arg.startswith('-'):
            return arg  # not flag or switch

        raise ArgumentError("Invalid switch '{}'".format(arg))

    key, value = matched.groups()
    value = True if value == '' else value
    return {key: value}


def _match_args(spec, args):
    ret_args, ret_kwargs = [], {}

    for arg in args:
        arg = _parse_one_arg(arg)

    return ret_args, ret_kwargs


def match(func, *, args=None, **options):
    args = args if args is not None else sys.argv[1:]
    if isinstance(func, SimpleNamespace):
        spec = func
    else:
        spec = parse(func, **options)

    matcher_args, matcher_kwargs = _match_args(spec, args)

    # TODO: validate matcher

    # From Clime
    # -(?P<long>-)?(?P<key>(?(long)[^ =,]+|.))[ =]?(?P<meta>[^ ,]+)?

    return matcher_args, matcher_kwargs


def run(func, *, args=None, **options):

    spec = parse(func, args=args, **options)
    matcher = match(spec, args=args, **options)
    validate(func, matcher)

    return func()
