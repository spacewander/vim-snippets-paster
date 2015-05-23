import pytest

from .snippet import Snippet
from .ultisnips import (handle_embeded_variables,
                        parse, build, convert_embeded_variables)
from .ultility import NotImplementFeatureException

author = "who is `g:snips_author`"
author_body = "who is `$author`"
email = "what is `g:snips_author_email`"
email_body = "what is `$email`"

def test_author():
    assert handle_embeded_variables(author) == author_body

def test_email():
    assert handle_embeded_variables(email) == email_body


def test_convert_author():
    assert convert_embeded_variables(author_body) == author

def test_convert_email():
    assert convert_embeded_variables(email_body) == email

def test_embed_sh_code():
    with pytest.raises(NotImplementFeatureException):
        handle_embeded_variables('`ls -l`')

def test_embed_py_code():
    with pytest.raises(NotImplementFeatureException):
        handle_embeded_variables('`!p snip.rv = (75-2*len(t[1]))*' '`')

def test_embed_viml_code():
    assert handle_embeded_variables('`!v indent(".")`') == '`indent(".")`'

def test_convert_viml_code():
    assert convert_embeded_variables('`indent(".")`') == '`!v indent(".")`'

normal_snippet = """snippet t
true ${VISUAL}
endsnippet"""

if_snippet = """snippet if "if ..." w
if ${2:[[ ${1:condition} ]]}; then
    ${0:#statements}
fi
endsnippet"""

if_snippet_after = """if ${2:[[ ${1:condition} ]]}; then
    ${0:#statements}
fi"""

def parse_snippet(input):
    return parse(input.split('\n'), {})

def test_parse():
    snippet = parse_snippet(normal_snippet)
    assert snippet.name == 't'
    assert snippet.description == ''
    assert snippet.body == 'true $VISUAL'

def test_description():
    snippet = parse_snippet(if_snippet)
    assert snippet.name == 'if'
    assert snippet.description == 'if ...'
    assert snippet.u_options == set('w')
    assert snippet.body == if_snippet_after

quote_snippet = """snippet t"quote"t
quote
endsnippet"""

def test_quote():
    snip = parse_snippet(quote_snippet)
    assert snip.name == '"quote"'
    assert snip.description == ''

ws_snippet = """snippet !ws ws!
endsnippet"""

def test_whitespace():
    snip = parse_snippet(ws_snippet)
    assert snip.name == 'ws ws'

expr_snippet = """snippet expr "" "expr" we
expr
endsnippet"""

def test_expr():
    snip = parse_snippet(expr_snippet)
    assert snip.u_context == "expr"

build_snippet = Snippet('snipmate', name='if',
                        body='if ${1:value} else ${2}',
                        description='if snippet')

build_snippet_after = """snippet if "if snippet"
if ${1:value} else ${2}
endsnippet"""

def test_build():
    assert build(build_snippet) == build_snippet_after

