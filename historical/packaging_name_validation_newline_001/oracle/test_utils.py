import pytest
from packaging.tags import Tag
from packaging.utils import InvalidName, InvalidSdistFilename, InvalidWheelFilename, canonicalize_name, canonicalize_version, is_normalized_name, parse_sdist_filename, parse_wheel_filename
from packaging.version import Version

def test_canonicalize_name_invalid():
    for name, expected in [('_not_legal', '-not-legal'), ('hi\n', 'hi\n'), ('\nhi', '\nhi'), ('h\ni', 'h\ni'), ('hi\r', 'hi\r'), ('\rhi', '\rhi'), ('h\ri', 'h\ri')]:
        with pytest.raises(InvalidName):
            canonicalize_name(name, validate=True)
        assert canonicalize_name(name) == expected
