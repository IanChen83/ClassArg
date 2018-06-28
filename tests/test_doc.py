from types import SimpleNamespace
import textwrap

import pytest

import classarg._doc as doc


def _gen_parse_doc_testcase():
    tiny_str = """Loren ipsum dolor sit amet."""
    long_str = (
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris\n'
        'sed urna quis ante luctus sodales a vel felis.'
    )

    # Single line, without arg_docs
    str0 = """Loren ipsum dolor sit amet."""
    expect0 = dict(intros=[tiny_str])

    # Multiple sections, without arg_docs
    str1 = """Loren ipsum dolor sit amet.

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.
        """
    expect1 = dict(intros=[tiny_str, long_str])

    # Multiple sections, arg_docs
    # key not found in the spec
    str2 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.

        aaa:  Loren ipsum dolor sit amet.
        xxx:  pass
        bbb:  Loren ipsum dolor sit amet.
        ccc:  Loren ipsum dolor sit amet.
        """
    expect2 = dict(intros=[long_str],
                   arg_docs=dict(aaa=tiny_str,
                                 bbb=tiny_str,
                                 ccc=tiny_str,
                                 xxx='pass'))

    # Ignore keys not found in the spec
    # Recognize continued lines
    str3 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.

        aaa:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        xxx:  --pass
              sed urna quis ante luctus sodales a vel felis.
        bbb:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        ccc:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        """
    expect3 = dict(intros=[long_str],
                   arg_docs=dict(aaa=long_str,
                                 bbb=long_str,
                                 ccc=long_str))

    # Multiple aliases
    str4 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.

        aaa:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        -d1:   --ddd
        -d2:   --ddd
        bbb:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        -e:   --eee
        ccc:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        """
    expect4 = dict(intros=[long_str],
                   arg_docs=dict(aaa=long_str,
                                 bbb=long_str,
                                 ccc=long_str),
                   aliases=dict(d1='ddd',
                                d2='ddd',
                                e='eee'))

    # Ignore invalid aliases
    str5 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.

        aaa:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        -a1:  --asdf
        -a1:  --aaa
        -a2:  --asdf asdfasdf
        --a2: --asdf asdfasdf
        bbb:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        -b:   --bbb asdf
              asdf
        ccc:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        """
    expect5 = dict(intros=[long_str],
                   arg_docs=dict(aaa=long_str,
                                 bbb=long_str,
                                 ccc=long_str))

    # Used alias
    str6 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.

        aaa:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
              sed urna quis ante luctus sodales a vel felis.
        bbb:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        ccc:  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
              sed urna quis ante luctus sodales a vel felis.
        -ddd: --ddd
        -ddd: --ddd
        """
    expect6 = ValueError()

    yield str0, expect0
    yield str1, expect1
    yield str2, expect2
    yield str3, expect3
    yield str4, expect4
    yield str5, expect5
    yield str6, expect6


@pytest.mark.parametrize('docstring, expect', list(_gen_parse_doc_testcase()))
def test_normalize_argument_docs(docstring, expect):
    # from this function
    # def func(aaa, bbb=False, *ccc, ddd: int, eee=2, **fff): pass
    spec = SimpleNamespace(
        args=['aaa', 'bbb'], varargs='ccc', varkw='fff', defaults=(1,),
        kwonlyargs=['ddd', 'eee'], kwonlydefaults={'eee': 2},
        annotations={'bbb': int, 'ddd': int, 'eee': int})

    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = doc.load_doc_hints(spec, docstring)
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)
    else:
        ret = doc.load_doc_hints(spec, docstring)
        for key, value in expect.items():
            assert getattr(ret, key) == value
