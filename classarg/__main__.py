from .utils import load_module


def main(module, dry_run=False, *arguments):
    """Load module to run

    module: module path
    dry_run: only parse input arguments and print them
    arguments: arguments of the imported module
    """
    module = load_module(module)


if __name__ == '__main__':
    pass
