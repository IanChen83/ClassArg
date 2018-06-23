NoneType = type(None)

_builtin = {int, float, bool, str, NoneType}
_meta = {type}
_supported = {
    int: 'int',
    float: 'float',
    bool: 'bool',
    str: 'str',
    NoneType: 'NoneType',
}


def get_type_hints(obj, globalns=None, localns=None):
    from inspect import getfullargspec
    spec = getfullargspec(obj)
    return spec.annotations


def _type_transform(obj):
    if obj is None:
        return NoneType

    elif obj in _builtin:
        return obj

    t = type(obj)
    if t in _meta:
        return t

    raise TypeError('Type {} is not supported'.format(t))


# The classes have two requirements:
# 1. str(cls.__origin__) == typing.Class
# 2. type(cls.__args__) is tuple
class _CollectionType(type):
    __slots__ = tuple()

    @classmethod
    def __prepare__(mcs, name, bases):
        origin = 'typing.' + name
        slots = ('__args__', )

        def transform(instance, params):
            instance.__args__ = params
            return instance

        return dict(__origin__=origin,
                    __slots__=slots,
                    __transform__=transform)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        # Register itself
        _supported[cls] = cls.__origin__
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


class Union(metaclass=_CollectionType):
    def __transform__(self, params):
        param_len = len(params)
        if param_len == 0:
            raise TypeError('Cannot instantiate typing.Union')

        elif param_len == 1:
            return params[0]

        print(params)
        params = Union._flatten_params(params)
        print(params)
        self.__args__ = params
        return self

    @staticmethod
    def _flatten_params(params):
        new_params = []
        for p in params:
            if isinstance(p, Union):
                new_params.extend(p.__args__)
            else:
                new_params.append(p)

        return tuple(new_params)


class Optional(metaclass=_CollectionType):
    def __transform__(self, params):
        if len(params) != 1:
            raise TypeError((
                'Optional[t] requires a single type.'
                'Got ' + params))

        return Union(params + (NoneType, ))
