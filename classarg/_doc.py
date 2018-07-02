import re
from textwrap import dedent
from collections import namedtuple

from .utils import PeekIter

__all__ = (
    'parse_docstring',
    'parse_arg_entries',
)


_Section = namedtuple('_Section', 'header contents')


_arg_doc_pattern = re.compile(
    r'^\s*([^\d\W]\w*)(,[^:]?\s*-{,2}([^\d\W]\w*))*\s*:\s*(.+)')
_arg_pattern = re.compile(r'-{,2}([^\d\W]\w*)')
_header_pattern = re.compile(r'^(?!\s)(.+):\s*$')


def parse_arg_entries(lines):
    """Parse augument entries into structured data.

    Augument entries always have the following format

    ```
       arg1, --alias_of_arg1: the description of arg1
       arg2: the description of arg2,
             the second line.
    ```

    Returns:
       A tuple (docs, aliases), where docs is a dictionary mapping arg names
       to their description, and aliases maps aliases to their source name.
    """
    docs, aliases = {}, {}
    last_key = None

    for line in lines:
        matched = _arg_doc_pattern.match(line)
        if matched is not None:
            keys, *value = line.split(':', maxsplit=1)
            key, *others = _arg_pattern.findall(keys)
            value = ':'.join(value)

            docs[key] = value.strip()
            for other in others:
                aliases[other] = key
            last_key = key
            continue

        if last_key in docs:
            line = ' ' + line.strip()
            docs[last_key] = '{}\n{}'.format(
                docs[last_key].rstrip(), line.lstrip())
            continue

        # TODO: warning
        last_key = None

    return docs, aliases


def _get_indent(line):
    for i, s in enumerate(line):
        if not s.isspace():
            return i
    return len(line)


def _consume_empty(it):
    while it.has_next() and not it.peek():
        next(it)


def _consume_description(it):
    contents = []
    while it.has_next():
        line = it.peek()
        if not line:
            return _Section(None, contents)
        contents.append(next(it))

    return _Section(None, contents)


def _consume_section(it, section_indent):
    header = _header_pattern.search(next(it)).groups()[0]
    contents = []
    while it.has_next():
        line = it.peek()
        if not line:
            next(it)
            continue

        indent = _get_indent(line)
        if indent <= section_indent:
            return _Section(header, contents)
        contents.append(next(it))

    return _Section(header, contents)


def parse_docstring(docstring):
    """Parse docstring into structured data.

    We parse docstring based on the guide
    https://github.com/google/styleguide/blob/gh-pages/pyguide.md
    but we make a few adjustments:

    1. the guide only defines three special sections _Args_, _Returns_, and
       _Raises_. We allow any name for section headers.

    2. If the last paragraph is _Args_ section, and there's no paragraph that
       has section header, the section header can be omitted.

    Returns:
        An object of type List[_Section], each section has two attributes
        header and contents. Contents are of type List[str], and header can
        be either None or a str.

        Note that the indention of contents relative to their header is
        preserved.
    """
    # dedent docstring correctly
    first_line, *docstring = docstring.split('\n', maxsplit=1)
    if not docstring:
        return [_Section(None, [first_line])]
    lines = [first_line] + dedent(docstring[0]).split('\n')

    ret = []
    line_iter = PeekIter(lines)
    _consume_empty(line_iter)

    while line_iter.has_next():
        line = line_iter.peek()

        if _header_pattern.search(line):
            section = _consume_section(line_iter, _get_indent(line))
        else:
            section = _consume_description(line_iter)

        ret.append(section)
        _consume_empty(line_iter)

    # Deal with the last section
    if ret and all(sec.header is None for sec in ret):
        section = ret.pop()
        if any(parse_arg_entries(section.contents)):
            section = _Section('Args', section.contents)
        ret.append(section)

    return ret
