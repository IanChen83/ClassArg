import pytest

from classarg._doc import parse_docstring, _Section


def _gen_parse_doc_testcase():
    tiny_str = """Loren ipsum dolor sit amet."""
    long_str = (
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris\n'
        'sed urna quis ante luctus sodales a vel felis.'
    )
    args_str = """aaa:  Loren ipsum dolor sit amet."""

    # Single line, without argument_sections
    str0 = """Loren ipsum dolor sit amet."""
    expect0 = [_Section(None, [tiny_str])]

    # Multiple line, without argument_sections
    str1 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.
        """
    expect1 = [_Section(None, long_str.split('\n'))]

    # Multiple sections, without argument_sections
    str2 = """Loren ipsum dolor sit amet.

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.
        """
    expect2 = [_Section(None, [tiny_str]),
               _Section(None, long_str.split('\n'))]

    # Multiple sections, argument_sections
    # additional blank line
    str3 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.





        aaa:  Loren ipsum dolor sit amet.
        """
    expect3 = [_Section(None, long_str.split('\n')),
               _Section('Args', [args_str])]

    # Multiple sections, argument_sections
    # headers, unrecognize header
    str4 = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris
        sed urna quis ante luctus sodales a vel felis.

        Returns:
            aaa:  Loren ipsum dolor sit amet.

        aaa:  Loren ipsum dolor sit amet.
        """
    expect4 = [_Section(None, long_str.split('\n')),
               _Section('Returns', ['    ' + args_str]),
               _Section(None, [args_str])]

    yield str0, expect0
    yield str1, expect1
    yield str2, expect2
    yield str3, expect3
    yield str4, expect4


@pytest.mark.parametrize('docstring, expect', list(_gen_parse_doc_testcase()))
def test_normalize_argument_docs(docstring, expect):
    if isinstance(expect, Exception):
        with pytest.raises(Exception) as e_info:
            ret = parse_docstring(docstring)
            print(ret)  # only print if not raising error

        assert isinstance(expect, e_info.type)
    else:
        sections = parse_docstring(docstring)
        assert sections == expect
