# Some code are modified from cpython's typing module.
from .utils import compatible_with

__all__ = (
    'normalize_type',
    'load_type_hints',
    'Union',
    'Optional',
    'List',
    'Set',
    'Tuple',
)


NoneType = type(None)

_builtin = {int, float, bool, str}
_meta = set()
_supported_names = {
    'int': int,
    'float': float,
    'bool': bool,
    'str': str,
    'None': None,
    'NoneType': NoneType,
}

# Starts from python 3.7,
#   Tuple[...].__origin__ = tuple
#   List[...].__origin__ = list
#   Set[...].__origin__ = set
#
# so we have to maps thme to
#   Tuple[...].__origin__ = Tuple
#   List[...].__origin__ = List
#   Set[...].__origin__ = Set
_aux_mapping = {}


def _eval_type_from_str(obj):
    try:
        code = compile(obj, '<string>', 'eval')
        ret = eval(code, dict(__builtin__=None,
                              **_supported_names))
        return normalize_type(ret)

    except (SyntaxError, NameError):
        raise TypeError('Failed to parse type from string')


def normalize_type(obj):
    if obj is None or obj is NoneType:
        return NoneType

    elif obj in _builtin:
        return obj

    elif isinstance(obj, str):
        return _eval_type_from_str(obj)

    elif hasattr(obj, '__origin__'):
        if obj.__origin__ in _aux_mapping:
            # Clone obj because it's not good to modify
            # obj.__origin__ directly.
            origin, args = _aux_mapping[obj.__origin__], obj.__args__
            obj = origin[args]
            obj.__origin__ = origin

        if obj.__origin__ in _meta:  # must be instance of meta types
            obj.__args__ = tuple(normalize_type(arg)
                                 for arg in obj.__args__)
            return obj

    raise TypeError('Failed to normalize {}'.format(obj))


def infer_default_type(value):
    """Infer type hint from default value.

    Returning None means failed inferal.
    """
    t = type(value)
    if t in _builtin:
        return t
    elif t is tuple:
        return Tuple[tuple(infer_default_type(v)
                           for v in value)]

    return None


def load_type_hints(spec):
    annotations = spec.annotations
    spec_defaults = spec.defaults or tuple()
    spec_kwonlydefaults = spec.kwonlydefaults or {}
    defaults = dict(spec_kwonlydefaults,
                    **{k: v for k, v in zip(reversed(spec.args),
                                            reversed(spec_defaults))})

    ret = {}
    for key, value in annotations.items():
        try:
            ret[key] = normalize_type(value)
        except TypeError:
            pass

    for key, value in defaults.items():
        if key in ret and value is None:
            ret[key] = Optional[ret[key]]

        elif key not in ret:
            try:
                ret[key] = infer_default_type(value)
            except TypeError:
                pass

    spec.annotations = ret


# The classes have two requirements:
# 1. cls.__origin__ is typing.Class
# 2. type(cls.__args__) is tuple
if compatible_with(3, 5):  # has typing module
    import typing
    from typing import Union, Optional, List, Set, Tuple
    for name in ('Union', 'Optional', 'List', 'Set', 'Tuple'):
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

    class _CollectionType(type):
        __slots__ = tuple()

        @classmethod
        def __prepare__(mcs, name, bases, **kwargs):
            slots = ('__args__', '__origin__')

            def _repr(instance):
                args = ", ".join([_type_repr(a) for a in instance.__args__])
                return '{}[{}]'.format(instance.__origin__, args)

            def eq(instance, other):
                if not (hasattr(other, '_name') and
                        hasattr(other, '__args__')):
                    return False
                return (instance._name == other._name and
                        instance.__args__ == other.__args__)

            def _hash(instance):
                return hash((instance._name, ) + instance.__args__)

            return dict(__slots__=slots,
                        __repr__=_repr,
                        __hash__=_hash,
                        __eq__=eq)

        def __new__(cls, name, bases, attrs, **kwargs):
            return super().__new__(cls, name, bases, attrs)

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
                params = (normalize_type(params), )
            else:
                params = tuple(normalize_type(p) for p in params)

            ret = super().__call__()
            return ret.__transform__(params)

        def __call__(cls, params):
            raise TypeError('Cannot directly intialize special typing classes')

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
            waiting, new_params = [], []
            waiting.extend(params)
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

            return Union[params + (NoneType, )]

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

    class Tuple(metaclass=_CollectionType):
        def __transform__(self, params):
            self.__args__ = params
            return self

_aux_mapping[list] = List
_aux_mapping[set] = Set
_aux_mapping[tuple] = Tuple
