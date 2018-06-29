import re
from textwrap import dedent, TextWrapper
from collections import defaultdict


def _is_valid_alias_source(spec, key):
    return key != spec.varkw


def _is_valid_arg(spec, key):
    return (key in spec.args or
            key == spec.varargs or
            key == spec.varkw or
            key in spec.kwonlyargs)


arg_doc_pattern = re.compile(r'^-{,2}([^\d\W]\w*):\s{1,}(.+)')
alias_pattern = re.compile(r'^-{,2}([^\d\W]\w*):\s{1,}(-{1,2}[^\d\W]\w*)$')


def _normalize_argument_docs(spec, section):
    """Parse arg docs into entries and aliases

    An arg entry has key in spec.{args, kwonlydefaults, varargs, varkw}
    and value wrapped in multi-lines. For instance:

        aa:  the meaning of aa, wrapped in multiple lines. It
             doesn't necessarily need to be indented, though.

    An arg alias has key and value fulfilling more strict rules. The value
    should be in the spec. For instance:

        -a:  --aa

    The action when users specify -a in the CLI depends on the role and type
    of --aa.

    If kwargs exists, there can be aliases in the format of arg entry. These
    aliases will be added into available switches. If there's no kwargs, this
    type of alias is not allowed.
    """
    waiting = section.split('\n')
    docs, aliases = {}, {}
    last_key = None

    while waiting:
        line = waiting.pop(0).rstrip()
        matched = arg_doc_pattern.search(line) or alias_pattern.search(line)
        if matched is None:
            if last_key in docs:
                line = ' ' + line.strip()
                docs[last_key] = '{}\n{}'.format(
                    docs[last_key].rstrip(), line.lstrip())
        else:
            key, value = matched.groups()
            if value.startswith('-'):
                # for alias,
                # argument_docs values don't start with '-'
                key, value = key.lstrip('-'), value.lstrip('-')
                if _is_valid_arg(spec, key):
                    raise ValueError(
                        "Key '{}' for aliasing has bee used.".format(key))

                if _is_valid_alias_source(spec, value):
                    aliases[key] = value
                    last_key = key
                else:
                    last_key = None
            else:
                if _is_valid_arg(spec, key):
                    docs[key] = value
                    last_key = key
                elif spec.varkw is not None:
                    spec.kwonlyargs.append(key)
                    spec.kwonlydefaults[key] = False
                    spec.annotations[key] = bool
                    docs[key] = value
                    last_key = key
                else:
                    last_key = None

    return docs, aliases


candidate_headers_ending = (
    'arg:',
    'args:',
    'argument:',
    'arguments:',
    'flag:',
    'flags:',
    'switch:',
    'switches:',
)
def load_doc_hints(spec, docstring): # noqa
    spec.descriptions = []
    spec.argument_docs = {}
    spec.aliases = {}

    sections = [dedent(sec).strip()
                for sec in docstring.split('\n\n')]

    for section in sections:
        if not section:
            continue

        original_section = section
        header, *contents = section.split('\n', maxsplit=1)
        if any(header.lower().endswith(item)
               for item in candidate_headers_ending) and contents:
            section = dedent(contents[0])
            print(section)

        argument_docs, aliases = _normalize_argument_docs(spec, section)

        if not argument_docs and not aliases:
            spec.descriptions.append(original_section)
        else:
            spec.argument_docs.update(**argument_docs)
            spec.aliases.update(**aliases)

    return spec


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

    if hasattr(spec, 'argument_docs') and hasattr(spec, 'aliases'):
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
            if key not in spec.argument_docs:
                continue
            doc = spec.argument_docs[key]

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
