import pytest

from .snipmate import format_placeholders, build
from .snippet import Snippet
from .ultility import UnsupportFeatureException

if_snippet = Snippet('ultisnips', name='if',
                     body='if ...', description='if snippet')

if_snippet_after = """snippet if if snippet
\tif ..."""

def test_format_placeholders():
    lines = ["it is ${VISUAL}", 'and ${0}']
    assert format_placeholders(lines) == ["it is $VISUAL", 'and $0']

def test_build():
    assert build(if_snippet) == if_snippet_after

def test_whitespace_name():
    whitespace_snippet = Snippet(name='with some', type='', body='')
    with pytest.raises(UnsupportFeatureException):
        build(whitespace_snippet)

