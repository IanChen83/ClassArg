import re
from textwrap import dedent, TextWrapper
from collections import defaultdict
from types import SimpleNamespace as namespace

__all__ = (
    'parse_docstring',
)

arg_doc_pattern = re.compile(r'^-{,2}([^\d\W]\w*):\s{1,}(.+)')
alias_pattern = re.compile(r'^-{,2}([^\d\W]\w*):\s{1,}-{1,2}([^\d\W]\w*)$')
def _parse_section(section): # noqa
    waiting = section.split('\n')
    docs = {}
    docs, aliases = {}, {}
    last_key = None

    while waiting:
        line = waiting.pop(0).strip()
        matched = alias_pattern.search(line)
        if matched is not None:
            key, value = matched.groups()
            aliases[key] = value
            last_key = None
            continue

        matched = arg_doc_pattern.search(line)
        if matched is not None:
            key, value = matched.groups()
            docs[key] = value
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


section_header_pattern = re.compile(r'\s*(.+):\s*$')
def parse_docstring(docstring): # noqa
    descriptions = []
    sections = []

    paragraphs = [dedent(sec).strip()
                  for sec in docstring.split('\n\n')]

    for para in paragraphs:
        if not para:
            continue

        original_para = para
        header, *contents = para.split('\n', maxsplit=1)
        if not contents:
            descriptions.append(header)
            continue

        header = section_header_pattern.search(header)
        if header is not None:
            header = header.groups()[0].title()
            para = dedent(contents[0])

        docs, aliases = _parse_section(para)

        if docs or aliases:
            sections.append(namespace(header=header,
                                      docs=docs,
                                      aliases=aliases))
        else:
            descriptions.append(original_para)

    return descriptions, sections


def _get_one_argument_doc(key, doc, width, tabstop):
    key = '  ' + key + '  '

    if len(key) > tabstop:
        wrapper = TextWrapper(
            initial_indent=' '*tabstop,
            width=width-tabstop, subsequent_indent=' '*tabstop)
        return key.rstrip() + '\n' + '\n'.join(wrapper.wrap(doc))
    else:
        wrapper = TextWrapper(
            initial_indent=' '*(tabstop-len(key)),
            width=width-tabstop, subsequent_indent=' '*tabstop)

        return key + '\n'.join(wrapper.wrap(doc))


def _prefix_key(key):
    return '-' + key if len(key) == 1 else '--' + key


def get_normalized_docstring(spec, width=70, tabstop=16):
    sections = []
    if hasattr(spec, 'descriptions'):
        sections.append('\n\n'.join(text for text in spec.descriptions))

    if hasattr(spec, 'argument_sections') and hasattr(spec, 'aliases'):
        items = ['Arguments:']
        aliases = defaultdict(list)
        for alias, source in spec.aliases.items():
            aliases[source].append(_prefix_key(alias))

        candidates = []
        candidates.extend(spec.args)
        if spec.varargs:
            candidates.append(spec.varargs)
        candidates.extend(spec.kwonlyargs)

        for key in candidates:
            if key not in spec.argument_sections:
                continue
            doc = spec.argument_sections[key]

            name = key
            if name in spec.kwonlyargs:
                key = _prefix_key(key)

            if name in aliases:
                aliases[key].sort(key=len, reverse=True)
                key = '{}, {}'.format(
                    key, ', '.join(aliases[name]))

            items.append(_get_one_argument_doc(key, doc, width, tabstop))

        sections.append('\n'.join(items))

    return '\n\n'.join(sections)
