import sys


def is_newer_sys_version(major, minor=0, micro=0):
    info = sys.version_info
    return (info.major, info.minor, info.micro) >= (major, minor, micro)


# load_module(path)
if is_newer_sys_version(3, 4):
    import importlib

    def load_module(path):
        spec = importlib.util.spec_from_file_location('target_module', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module
else:
    def load_module(path):
        raise NotImplementedError(
            'This module only support Python version >= 3.4')


# get_type_hints(obj, globalns=None, localns=None)
if is_newer_sys_version(3, 5):
    from typing import get_type_hints

else:
    def get_type_hints(obj, globalns=None, localns=None):
        if hasattr(obj, 'annotations'):
            return dict(obj.__annotations__)

        return dict()
