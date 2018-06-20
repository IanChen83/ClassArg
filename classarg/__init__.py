import sys

from .core import parse, match, run

__all__ = ('parse', 'run', 'match')


# sys.modules[__name__].__call__ = run


# The following variables will be used in PyPI index.
__name__ = 'classarg'

__author__ = 'Ian Chen'

__license__ = 'MIT'

__version__ = '0.0.2'

__email__ = 'patrickchen1994@gmail.com'

# Prototype, Development, or Production
__status__ = 'Prototype'
