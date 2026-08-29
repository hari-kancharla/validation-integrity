# ---- tests/test_utils.py ----
import pytest
from packaging.tags import Tag
from packaging.utils import InvalidName, InvalidSdistFilename, InvalidWheelFilename, canonicalize_name, canonicalize_version, is_normalized_name, parse_sdist_filename, parse_wheel_filename
from packaging.version import Version

def test_canonicalize_name():
    for name, expected in [('foo', 'foo'), ('Foo', 'foo'), ('fOo', 'foo'), ('foo.bar', 'foo-bar'), ('Foo.Bar', 'foo-bar'), ('Foo.....Bar', 'foo-bar'), ('foo_bar', 'foo-bar'), ('foo___bar', 'foo-bar'), ('foo-bar', 'foo-bar'), ('foo----bar', 'foo-bar')]:
        assert canonicalize_name(name) == expected

def test_is_normalized_name():
    for name, expected in [('foo', 'foo'), ('Foo', 'foo'), ('fOo', 'foo'), ('foo.bar', 'foo-bar'), ('Foo.Bar', 'foo-bar'), ('Foo.....Bar', 'foo-bar'), ('foo_bar', 'foo-bar'), ('foo___bar', 'foo-bar'), ('foo-bar', 'foo-bar'), ('foo----bar', 'foo-bar')]:
        assert is_normalized_name(expected)
        if name != expected:
            assert not is_normalized_name(name)

def test_canonicalize_version():
    for version, expected in [(Version('1.4.0'), '1.4'), ('1.4.0', '1.4'), ('1.40.0', '1.40'), ('1.4.0.0.00.000.0000', '1.4'), ('1.0', '1'), ('1.0+abc', '1+abc'), ('1.0.dev0', '1.dev0'), ('1.0.post0', '1.post0'), ('1.0a0', '1a0'), ('1.0rc0', '1rc0'), ('100!0.0', '100!0'), ('lolwat', 'lolwat'), ('1.0.1-test7', '1.0.1-test7')]:
        assert canonicalize_version(version) == expected

def test_canonicalize_version_no_strip_trailing_zero():
    for version in ['1.4.0', '1.0']:
        assert canonicalize_version(version, strip_trailing_zero=False) == version

def test_parse_sdist_filename():
    for filename, name, version in [('foo-1.0.tar.gz', 'foo', Version('1.0')), ('foo-1.0.zip', 'foo', Version('1.0'))]:
        assert parse_sdist_filename(filename) == (name, version)
