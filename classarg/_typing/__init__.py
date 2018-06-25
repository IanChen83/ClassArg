from ..utils import compatible_with

__all__ = (
    'get_type_hints',
    'Union',
    'Optional',
    'List',
    'Set',
)

if compatible_with(3, 5):
    from typing import get_type_hints as _get_type_hints, Union, Optional, List, Set

else:
    from .py34 import get_type_hints as _get_type_hints, Union, Optional, List, Set

# Only support python >= 3.5
# from typing import get_type_hints as _get_type_hints, Union, Optional, List, Set

# Only support python 3.4
# from .py34 import get_type_hints as _get_type_hints, Union, Optional, List, Set


def get_type_hints(obj):
    return _get_type_hints(obj)
