from .utils import compatible_with


# load_module(path)
if compatible_with(3, 4):
    import importlib

    def load_module(path):
        spec = importlib.util.spec_from_file_location('target_module', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module
else:
    raise NotImplementedError(
        'This module only support Python version >= 3.4')


def main(module, dry_run=False, *arguments):
    """Load module to run

    module: module path
    dry_run: only parse input arguments and print them
    arguments: arguments of the imported module
    """
    module = load_module(module)


if __name__ == '__main__':
    pass
