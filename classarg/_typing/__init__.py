from ..utils import compatible_with

# from .py34 import *

if compatible_with(3, 5):
    pass

else:
    from .py34 import get_type_hints, Union, Optional
