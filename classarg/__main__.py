import sys
import importlib

from . import match

_candidate_func_names = ['main', 'Main']


def is_newer_sys_version(major, minor=0, micro=0):
    info = sys.version_info
    return (info.major, info.minor, info.micro) >= (major, minor, micro)


if is_newer_sys_version(3, 4):
    def load_module(path):
        spec = importlib.util.spec_from_file_location('target_module', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

elif is_newer_sys_version(3, 3):
    def load_module(path):
        module = importlib.machinery.SourceFileLoader(
            'target_module', path).load_module()

        return module

else:
    raise NotImplementedError('This module only support Python version >= 3.')


def main(module, dry_run=False, *arguments):
    """Load module to run

    module: module path
    dry_run: only parse input arguments and print them
    arguments: arguments of the imported module
    """
    module = load_module(module)


if __name__ == '__main__':
    res = match(main)
    if res.arguments:
        res.arguments.pop(0)

    res.module(*res.arguments)
