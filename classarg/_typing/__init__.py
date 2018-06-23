from ..utils import compatible_with

from .py34 import get_type_hints, Union, Optional

__all__ = (
    'get_type_hints',
    'Union',
    'Optional',
)

# if compatible_with(3, 5):
#     from typing import get_type_hints, Union, Optional

# else:
#     from .py34 import get_type_hints, Union, Optional
