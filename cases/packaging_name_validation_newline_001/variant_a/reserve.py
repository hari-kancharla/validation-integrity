# ---- reserve/test_utils_more.py ----
import pytest
from packaging.tags import Tag
from packaging.utils import InvalidName, InvalidSdistFilename, InvalidWheelFilename, canonicalize_name, canonicalize_version, is_normalized_name, parse_sdist_filename, parse_wheel_filename
from packaging.version import Version

def test_parse_wheel_filename():
    for filename, name, version, build, tags in [('foo-1.0-py3-none-any.whl', 'foo', Version('1.0'), (), {Tag('py3', 'none', 'any')}), ('some_PACKAGE-1.0-py3-none-any.whl', 'some-package', Version('1.0'), (), {Tag('py3', 'none', 'any')}), ('foo-1.0-1000-py3-none-any.whl', 'foo', Version('1.0'), (1000, ''), {Tag('py3', 'none', 'any')}), ('foo-1.0-1000abc-py3-none-any.whl', 'foo', Version('1.0'), (1000, 'abc'), {Tag('py3', 'none', 'any')}), ('foo_bár-1.0-py3-none-any.whl', 'foo-bár', Version('1.0'), (), {Tag('py3', 'none', 'any')}), ('foo_bár-1.0-1000-py3-none-any.whl', 'foo-bár', Version('1.0'), (1000, ''), {Tag('py3', 'none', 'any')})]:
        assert parse_wheel_filename(filename) == (name, version, build, tags)

def test_parse_wheel_invalid_filename():
    for filename in ['foo-1.0.whl', 'foo-1.0-py3-none-any.wheel', 'foo__bar-1.0-py3-none-any.whl', 'foo#bar-1.0-py3-none-any.whl', 'foobar-1.x-py3-none-any.whl', 'foo-1.0-abc-py3-none-any.whl', 'foo-1.0-200-py3-none-any-junk.whl']:
        with pytest.raises(InvalidWheelFilename):
            parse_wheel_filename(filename)

def test_parse_sdist_invalid_filename():
    for filename in ['foo-1.0.xz', 'foo1.0.tar.gz', 'foo-1.x.tar.gz']:
        with pytest.raises(InvalidSdistFilename):
            parse_sdist_filename(filename)
