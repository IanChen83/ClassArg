"""This module defines validation rules that can be used as decorators to
transparently validate input arguments.

A rule always has the arguments `func` and `match`. For instance,
```
def rule([rule-specific args and kwargs], func, match):
    pass
```

Call `validation.register` to add a custom rule. Please don't define rules
with name starting with underscore.

"""

import sys
from types import ModuleType
from functools import wraps, partial


def _validation_rule(rule):
    """
    This function is used internally to wrap rule into a decorator factory at
    runtime.

    A decorator factory receives arguments and create a specific
    decorator. The decorator will append the rule into the list
    `main._classarg_val`.
    """
    @wraps(rule)
    def decorator_factory(*args, **kwargs):
        bound_rule = partial(rule, *args, **kwargs)

        def decorator(main):
            try:
                main._classarg_val.append(bound_rule)
            except AttributeError:
                setattr(main, '_classarg_val', [bound_rule])

            return main

        return decorator

    return decorator_factory


class ValidationModule(ModuleType):
    def __init__(self):
        super().__init__(__name__, __doc__)

        self._rules = {}

    def register(self, name, rule):
        self._rules[name] = _validation_rule(rule)

    def _internal_register(self, name, rule):
        setattr(self, name, _validation_rule(rule))

    def unregister(self, name):
        del self._rules[name]

    def __getattr__(self, name):
        if name not in self._rules:
            raise ValueError("Rule '{0}' is not registered.".format(name))

        return self._rules[name]


module = ValidationModule()
_support_funcs = (
    'one_of',
    'enforce_type',
    'at_least',
)

import classarg.validation_funcs as val_funcs # noqa
for func_name in _support_funcs:
    module._internal_register(
        func_name, getattr(val_funcs, func_name))


sys.modules[__name__] = module
