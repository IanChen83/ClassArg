from .utils import compatible_with

NoneType = type(None)

_builtin = {int, float, bool, str, NoneType}
_supported = {
    int: 'int',
    float: 'float',
    bool: 'bool',
    str: 'str',
    NoneType: 'NoneType',
}


if compatible_with(3, 5):
    from typing import get_type_hints, Union, Optional, List, Set, Tuple

    for t in (Union, List, Set, Tuple):
        _supported[t] = str(t)

else:   # python 3.4
    def get_type_hints(obj, globalns=None, localns=None):
        from inspect import getfullargspec
        spec = getfullargspec(obj)
        return spec.annotations

    def _type_check(obj):
        t = type(obj)
        return t not in _builtin and t in _supported

    class _CollectionType(type):
        __slots__ = None

        @classmethod
        def __prepare__(mcs, name, bases, **kwargs):
            __slots__ = ('__args__', )

            def transform(instance, params):
                instance.__args__ = params
                return instance

            return dict(__slots__=__slots__,
                        transform=transform)

        def __init__(cls, name, bases, attrs):
            super().__init__(name, bases, attrs)
            # Register itself
            _supported[cls] = 'typing.' + name

        def __getitem__(cls, params):
            if not isinstance(params, tuple):
                return cls(params)
            return cls(*params)

        def __call__(cls, *params):
            """Ensure that all inputs are supported types"""
            params = {p if p is not None else NoneType
                      for p in params}

            for p in params:
                if not _type_check(p):
                    raise TypeError(
                        'Type {} is not supported'.format(type(p)))

            ret = super().__call__()
            return cls.transform(ret, *params)

    class Union(metaclass=_CollectionType):
        @staticmethod
        def transform(instance, *params):
            param_len = len(params)
            if param_len == 0:
                raise TypeError('Cannot instantiate typing.Union')

            elif param_len == 1:
                return params[0]

            params = Union._flatten_params(params)
            instance.__args__ = params
            return instance

        @staticmethod
        def _flatten_params(params):
            new_params = set()
            for p in params:
                if isinstance(p, Union):
                    new_params.update(p.__args__)
                else:
                    new_params.add(p)

            return tuple(new_params)

    class Optional(metaclass=_CollectionType):
        def transform(instance, *params):
            if len(params) != 1:
                raise TypeError((
                    'Optional[t] requires a single type.'
                    'Got ' + params))

            return Union(NoneType, *params)
