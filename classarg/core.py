import sys
from inspect import getfullargspec, isfunction, ismethod, isclass, FullArgSpec


def validate(func, kwargs):
    if not hasattr(func, '_classarg_val'):
        return

    for validate_func in func._classarg_val:
        validate_func(func=func, match=kwargs)


def parse(func):
    if isfunction(func):
        spec = getfullargspec(func)

    elif ismethod(func):
        spec = getfullargspec(func)
        del spec.args[0]  # remove first argument

    elif isclass(func):
        raise NotImplementedError()

    elif hasattr(func, '__call__'):
        spec = getfullargspec(func)
        del spec.args[0]  # remove first argument

    else:
        raise TypeError('Could not determine the signature of ' + str(func))

    return spec.__class__(args=spec.args or [],
                          varargs=spec.varargs,
                          varkw=spec.varkw,
                          defaults=spec.defaults or tuple(),
                          kwonlyargs=spec.kwonlyargs or tuple(),
                          kwonlydefaults=spec.kwonlydefaults or {},
                          annotations=spec.annotations or {})


def match(func, args=None):
    if isinstance(func, FullArgSpec):
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
