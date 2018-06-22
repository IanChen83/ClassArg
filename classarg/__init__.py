from .core import parse, match, run
from .utils import is_newer_sys_version

__all__ = ('parse', 'run', 'match')


# The following variables will be used in PyPI index.
__name__ = 'classarg'

__author__ = 'Ian Chen'

__license__ = 'MIT'

__version__ = '0.0.2'

__email__ = 'patrickchen1994@gmail.com'

# Prototype, Development, or Production
__status__ = 'Prototype'


# classarg(func) only available in python >= 3.5
if is_newer_sys_version(3, 4):
    import sys

    class Main(sys.modules[__name__].__class__):
        __call__ = run

    sys.modules[__name__].__class__ = Main

else:
    import sys
    from types import ModuleType

    class Main(ModuleType):
        def __init__(self, module):
            super().__init__(module.__name__, module.__doc__)
            self._module = module

        def __getattr__(self, name):
            return getattr(self._module, name)

        def __call__(self, *args, **kwargs):
            return run(*args, **kwargs)

    sys.modules[__name__] = Main(sys.modules[__name__])
