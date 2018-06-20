import inspect

def getargspec(func):
    if inspect.isfunction(func):
        argspec = inspect.getfullargspec(func)

    elif inspect.ismethod(func):
        argspec = inspect.getfullargspec(func)
        del argspec.args[0]  # remove first argument

    elif inspect.isclass(func):
        if func.__init__ is object.__init__:  # to avoid an error
            argspec = inspect.getfullargspec(lambda self: None)
        else:
            argspec = inspect.getfullargspec(func.__init__)
        del argspec.args[0]  # remove first argument

    elif hasattr(func, '__call__'):
        argspec = inspect.getfullargspec(func.__call__)
        del argspec.args[0]  # remove first argument

    else:
        raise TypeError('Could not determine the signature of ' + str(func))

    return argspec
