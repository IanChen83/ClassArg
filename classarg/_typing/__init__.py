# Some code are modified from cpython's typing module.
from inspect import getfullargspec

from ..utils import compatible_with

__all__ = (
    'get_type_hints',
    'Union',
    'Optional',
    'List',
    'Set',
)


NoneType = type(None)

_builtin = {int, float, bool, str, NoneType}
_meta = set()
_supported_names = {
    'int': int,
    'float': float,
    'bool': bool,
    'str': str,
    'None': None,
    'NoneType': NoneType,
}


def _eval_type_from_str(obj):
    try:
        code = compile(obj, '<string>', 'eval')
        return eval(code, dict(__builtin__=None, **_supported_names))
    except (SyntaxError, NameError):
        raise TypeError('Failed to parse type from string')


def _type_transform(obj):
    if obj is None:
        return NoneType

    elif obj in _builtin:
        return obj

    if isinstance(obj, str):
        t = _eval_type_from_str(obj)
        if t in _builtin:
            return t
        elif hasattr(t, '__origin__') and t.__origin__ in _meta:
            return t
    else:
        t = type(obj)
        if t in _meta:
            return t

    raise TypeError('Type {} is not supported'.format(t))


def get_type_hints(obj, globalns=None, localns=None):
    spec = getfullargspec(obj)
    annotations = spec.annotations
    spec_defaults = spec.defaults or tuple()
    spec_kwonlydefaults = spec.kwonlydefaults or {}
    defaults = dict(**spec_kwonlydefaults,
                    **{k: v for k, v in zip(spec.args, spec_defaults)})

    ret = {}
    for key, value in annotations.items():
        ret[key] = _type_transform(value)

        if key in defaults and defaults[key] is None:
            ret[key] = Optional[ret[key]]

    return ret


if compatible_with(3, 5):
    import typing
    from typing import Union, Optional, List, Set
    for name in ('Union', 'Optional', 'List', 'Set'):
        cls = getattr(typing, name)
        _supported_names[name] = cls
        _meta.add(cls)

    _supported_names['typing'] = typing

else:
    def _type_repr(obj):
        if isinstance(obj, type):
            if obj.__module__ == 'builtins':
                return obj.__qualname__
        return repr(obj)

    # The classes have two requirements:
    # 1. str(cls.__origin__) == typing.Class
    # 2. type(cls.__args__) is tuple
    class _CollectionType(type):
        __slots__ = tuple()

        @classmethod
        def __prepare__(mcs, name, bases, **kwargs):
            slots = ('__args__', '__origin__')

            def _repr(instance):
                args = ", ".join([_type_repr(a) for a in instance.__args__])
                return '{}[{}]'.format(instance.__origin__, args)

            return dict(__slots__=slots,
                        __repr__=_repr)

        def __new__(mcs, name, bases, attrs, **kwargs):
            return super().__new__(mcs, name, bases)

        def __init__(cls, name, bases, attrs, **kwargs):
            super().__init__(name, bases, attrs)

            cls.__origin__ = cls
            cls._name = name

            if not hasattr(cls, '__transform__'):
                raise NotImplementedError(
                    "{} doesn\'t implement '__transform__' function".format(
                        cls))

            # Register itself
            if 'no_register' not in kwargs or not kwargs['no_register']:
                _supported_names[name] = cls
                _meta.add(cls)

        def __getitem__(cls, params):
            if not isinstance(params, tuple):
                params = (params, )

            return cls(params)

        def __call__(cls, params):
            """Ensure that all inputs are supported types"""
            params = tuple(_type_transform(p) for p in params)

            ret = super().__call__()
            return ret.__transform__(params)

        def __repr__(cls):
            return 'typing.' + cls._name

    class Union(metaclass=_CollectionType):
        def __transform__(self, params):
            params = Union._flatten_params(params)
            param_len = len(params)

            if param_len == 0:
                raise TypeError('Cannot instantiate typing.Union')

            elif param_len == 1:
                return params[0]

            self.__args__ = params
            return self

        @staticmethod
        def _flatten_params(params):
            waiting, new_params = [*params], []
            while waiting:
                p = waiting.pop(0)

                if isinstance(p, Union):
                    waiting.extend(p.__args__)
                elif p not in new_params:
                    new_params.append(p)

            return tuple(new_params)

    class Optional(metaclass=_CollectionType):
        def __transform__(self, params):
            if len(params) != 1:
                raise TypeError((
                    'Optional[t] requires a single type.'
                    'Got ' + params))

            return Union(params + (NoneType, ))

    class _SingleCollection(metaclass=_CollectionType, no_register=True):
        def __transform__(self, params):
            if len(params) != 1:
                raise TypeError((
                    'Too many parameters for List;'
                    ' got {}').format(params))

            self.__args__ = params
            return self

    class List(_SingleCollection):
        pass

    class Set(_SingleCollection):
        pass
