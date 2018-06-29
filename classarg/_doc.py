import re
from textwrap import dedent


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
                # arg_docs values don't start with '-'
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

        header, *contents = section.split('\n', maxsplit=1)
        old_section = section
        if any(header.lower().endswith(item)
               for item in candidate_headers_ending) and contents:
            section = dedent(contents[0])
            print(section)

        arg_docs, aliases = _normalize_argument_docs(spec, section)

        if not arg_docs and not aliases:
            spec.descriptions.append(old_section)
        else:
            spec.argument_docs.update(**arg_docs)
            spec.aliases.update(**aliases)

    return spec


def print_help(spec):
    pass
