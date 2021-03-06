import sys
from unittest import mock

import pytest

import classarg.utils as utils


def test_compatible_with():
    target_func = utils.compatible_with
    info = sys.version_info

    assert info.minor >= 4
    for minor in range(4, info.minor+1):
        assert target_func(info.major, minor)

    assert target_func(info.major, info.minor+1) is False
    assert target_func(info.major+1, 0) is False


def test_failed_load_module():
    with pytest.raises(Exception) as e_info:
        with mock.patch.object(sys, 'version_info') as v_info:
            v_info.major = 3
            v_info.minor = 3
            v_info.micro = 0

            utils.load_module('./')

        assert e_info.type is AttributeError
