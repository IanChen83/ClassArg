from types import SimpleNamespace as namespace

import pytest

import classarg._doc as doc


def _gen_parse_doc_testcase():
    tiny_str = """Loren ipsum dolor sit amet."""
    long_str = (
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris\n'
        'sed urna quis ante luctus sodales a vel felis.'
    )

    # Single line, without argument_sections
    str0 = """Loren ipsum dolor sit amet."""
    expect0 = namespace(descriptions=[tiny_str],
                        sections=[])

    # Multiple sections, without argument_sections
    str1 = """Loren ipsum dolor sit amet.

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.
        """
    expect1 = namespace(descriptions=[tiny_str, long_str],
                        sections=[])

    # Multiple sections, argument_sections
    # key not found in the spec
    # additional blank line
    str2 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.





        aaa:  Loren ipsum dolor sit amet.
        xxx:  pass
        bbb:  Loren ipsum dolor sit amet.
        ccc:  Loren ipsum dolor sit amet.
        """
    expect2 = namespace(descriptions=[long_str],
                        sections=[namespace(header=None,
                                            docs=dict(aaa=tiny_str,
                                                      bbb=tiny_str,
                                                      ccc=tiny_str,
                                                      xxx='pass'),
                                            aliases=dict())])

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
    expect3 = namespace(descriptions=[long_str],
                        sections=[namespace(header=None,
                                            docs=dict(aaa=long_str,
                                                      bbb=long_str,
                                                      ccc=long_str),
                                            aliases=dict(xxx='pass'))])

    # Multiple sections, argument_sections
    # headers, unrecognize header
    str4 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.

        Returns:
            xxx:  pass

        Arguments:
            aaa:  Loren ipsum dolor sit amet.
            bbb:  Loren ipsum dolor sit amet.
            ccc:  Loren ipsum dolor sit amet.

        Optional Arguments:
            xxx:  pass
        """
    expect4 = namespace(descriptions=[long_str],
                        sections=[namespace(header='Returns',
                                            docs=dict(xxx='pass'),
                                            aliases=dict()),
                                  namespace(header='Arguments',
                                            docs=dict(aaa=tiny_str,
                                                      bbb=tiny_str,
                                                      ccc=tiny_str),
                                            aliases=dict()),
                                  namespace(header='Optional Arguments',
                                            docs=dict(xxx='pass'),
                                            aliases=dict())])

    yield str0, expect0
    yield str1, expect1
    yield str2, expect2
    yield str3, expect3
    yield str4, expect4


@pytest.mark.parametrize('docstring, expect', list(_gen_parse_doc_testcase()))
def test_normalize_argument_docs(docstring, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = doc.load_doc_hints(docstring)
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)
    else:
        descriptions, sections = doc.parse_docstring(docstring)
        assert descriptions == expect.descriptions
        assert sections == expect.sections


def test_get_normalized_docstring():
    tiny_str = """Loren ipsum dolor sit amet."""
    long_str = (
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris\n'
        'sed urna quis ante luctus sodales a vel felis.'
    )
    return_str = 'Returns:\n  xxx:  pass'
    spec = namespace(
        args=['aaa', 'bbb'], varargs='ccc', varkw='fff', defaults=(1,),
        kwonlyargs=['ddd', 'eee', 'xxx'],
        kwonlydefaults={'eee': 2, 'xxx': False},
        annotations={'bbb': int, 'ddd': int, 'eee': int, 'xxx': bool},
        descriptions=[long_str, return_str],
        argument_sections=dict(aaa=tiny_str,
                               bbb=tiny_str,
                               ccc=tiny_str,
                               ddd=tiny_str,
                               xxx='pass'),
        aliases=dict(x='xxx'))

    expect7 = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
sed urna quis ante luctus sodales a vel felis.

Returns:
  xxx:  pass

Arguments:
  aaa           Loren ipsum dolor sit amet.
  bbb           Loren ipsum dolor sit amet.
  ccc           Loren ipsum dolor sit amet.
  --ddd         Loren ipsum dolor sit amet.
  --xxx, -x     pass"""
    expect8 = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
sed urna quis ante luctus sodales a vel felis.

Returns:
  xxx:  pass

Arguments:
  aaa      Loren ipsum dolor sit amet.
  bbb      Loren ipsum dolor sit amet.
  ccc      Loren ipsum dolor sit amet.
  --ddd    Loren ipsum dolor sit amet.
  --xxx, -x
           pass"""

    res = doc.get_normalized_docstring(spec)
    if res != expect7:
        print(res)
        assert res == expect7

    res = doc.get_normalized_docstring(spec, tabstop=11)
    if res != expect8:
        print(res)
        print(expect8)
        assert res == expect8
