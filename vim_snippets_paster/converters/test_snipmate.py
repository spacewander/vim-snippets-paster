import pytest

from .snipmate import parse, build, convert_embeded_variables
from .snippet import Snippet
from .ultility import NotImplementFeatureException, UnsupportFeatureException

indent_snippet = """snippet indent
\tindent1
\t\tindent2"""

indent_snippet_after = """indent1
\tindent2"""

def get_parsed_body(input):
    return parse(input.split('\n'), {}).body

def test_remove_indent():
    assert get_parsed_body(indent_snippet) == indent_snippet_after

Filename_snippet = """snippet Filename
\tlook at `some Filename('', 'default')`"""

def test_Filename():
    with pytest.raises(NotImplementFeatureException):
        get_parsed_body(Filename_snippet)

author_snippet = """snippet author
\t`g:snips_author`"""

author_snippet_after = "`$author`"

def test_handle_author():
    assert get_parsed_body(author_snippet) == author_snippet_after

if_snippet = Snippet('ultisnips', name='if',
                     body='if ...', description='if snippet')

if_snippet_after = """snippet if if snippet
\tif ..."""

def test_build():
    assert build(if_snippet) == if_snippet_after

def test_whitespace_name():
    whitespace_snippet = Snippet(name='with some', type='', body='')
    with pytest.raises(UnsupportFeatureException):
        build(whitespace_snippet)

def test_convert_author():
    author_body = "who is `$author`"
    assert convert_embeded_variables(author_body) == "who is `g:snips_author`"

def test_convert_email():
    email_body = "what is `$email`"
    with pytest.raises(UnsupportFeatureException):
        convert_embeded_variables(email_body)

