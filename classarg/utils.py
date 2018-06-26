import sys


def compatible_with(major, minor=0, micro=0):
    info = sys.version_info
    return (info.major, info.minor, info.micro) >= (major, minor, micro)
