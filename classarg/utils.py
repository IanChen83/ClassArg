import sys


def compatible_with(major, minor=0, micro=0):
    info = sys.version_info
    return (info.major, info.minor, info.micro) >= (major, minor, micro)


class PeekIter:
    __slots_ = ('_buffer', '_it')

    def __init__(self, iterable):
        # Use self._buffer is PeekIter to determine
        # if buffer is occupied.
        self._buffer = PeekIter
        self._it = iter(iterable)

    def __next__(self):
        if self._buffer is not PeekIter:
            ret, self._buffer = self._buffer, PeekIter
            return ret
        return next(self._it)

    def __iter__(self):
        return self

    def peek(self):
        if self._buffer is not PeekIter:
            return self._buffer

        self._buffer = next(self._it)
        return self._buffer

    def has_next(self):
        if self._buffer is not PeekIter:
            return True

        try:
            buffer = next(self._it)
        except StopIteration:
            return False

        self._buffer = buffer
        return True
