import pytest

from .ultility import NotImplementFeatureException
from .xptemplate import parse

if_snippet = """XPT if
if`$SPcmd^(`$SParg^`condition^`$SParg^)`$BRif^{
    `cursor^
}"""

if_snippet_after = """if ( ${1:condition} ) {
    $0
}"""

for_snippet = """XPT for hint=for\ (..;..;++)
for (`i^ = `0^; `i^ < `len^; ++`i^) {
    `cursor^
}"""

for_snippet_after = """for (${1:i} = ${2:0}; $1 < ${3:len}; ++$1) {
    $0
}"""

memset_snippet = """XPT memset " memset (..., ..., sizeof (...) ... )
memset(`$SParg^`buffer^,`$SPop^`what^0^,`$SPop^sizeof(`$SParg^`type^int^`$SParg^)`$SPop^*`$SPop^`count^`$SParg^)
"""

memset_snippet_after = """memset( ${1:buffer}, ${2:0}, sizeof( ${3:int} ) * ${4:count} )
"""

call_snippet = """XPT call wraponly=param " ..( .. )
`name^(`$SParg^`param^`$SParg^)"""

call_snippet_wraponly = """XPT call wraponly=param " ..( .. )
`name^(`$SParg^`param^`$SParg^)"""

call_snippet_after = """${1:name}( ${VISUAL} )"""

fcomment_snippet = """XPT fcomment
/**
 * @author : `$author^ | `$email^
 */
"""

fcomment_snippet_after = """/**
 * @author : `$author` | `$email`
 */
"""

alias_snippet = """XPT fr alias=for hint=for\ (..;..;++)
for (`i^ = `0^; `i^ < `len^; ++`i^) {
    `cursor^
}"""

synonym_snippet = """XPT fr synonym=for|fri hint=for\ (..;..;++)
for (`i^ = `0^; `i^ < `len^; ++`i^) {
    `cursor^
}"""

unescape_snippet = """XPT test " \$\(\ bla
test"""

unescape_hint_snippet = """XPT test hint=\$\(\ bla
test"""

def get_parsed_body(input):
    return parse(input.split('\n'), {})[0].body

def test_normal_snippet():
    assert get_parsed_body(if_snippet) == if_snippet_after

def test_mirror():
    assert get_parsed_body(for_snippet) == for_snippet_after

def test_placeholder():
    assert get_parsed_body(memset_snippet) == memset_snippet_after

def test_wrap():
    assert get_parsed_body(call_snippet) == call_snippet_after

def test_wraponly():
    assert get_parsed_body(call_snippet_wraponly) == call_snippet_after

def test_author():
    assert get_parsed_body(fcomment_snippet) == fcomment_snippet_after

def test_alias():
    snippets = parse(alias_snippet.split('\n'), {})
    assert snippets[1].name == 'for'

def test_synonym():
    snippets = parse(synonym_snippet.split('\n'), {})
    assert len(snippets) == 3
    assert snippets[1].name == 'for'

def get_parsed_description(input):
    return parse(input.split('\n'), {})[0].description

def test_description():
    assert get_parsed_description(memset_snippet) == \
            "memset (..., ..., sizeof (...) ... )"

def test_hint():
    assert get_parsed_description(for_snippet) == "for (..;..;++)"

def test_unescape():
    assert get_parsed_description(unescape_snippet) == "$(\ bla"
    assert get_parsed_description(unescape_hint_snippet) == "$( bla"

hidden_snippet = """XPT some hidden
the answer to `life, the universe and everything^ is `42^"""

include_snippet = """XPT include
it includes '`:some:^' and `other^"""

include_snippet2 = """XPT include
it includes '`Include:some^' and `other^"""

include_snippet_after = \
        "it includes 'the answer to ${1:life, the universe and everything} is ${2:42}' and ${3:other}"

def test_hidden():
    ct = {}
    out = parse(hidden_snippet.split('\n'), ct)
    assert len(out) == 0

def test_include():
    ct = {}
    parse(hidden_snippet.split('\n'), ct)
    res = parse(include_snippet.split('\n'), ct)[0].body
    assert res == include_snippet_after
    # another include syntax
    res = parse(include_snippet2.split('\n'), ct)[0].body
    assert res == include_snippet_after

def test_include_exception():
    ct = {} # no hidden template existed
    with pytest.raises(NotImplementFeatureException):
        parse(include_snippet.split('\n'), ct)

filehead_snippet = """XPT filehead
XSET cursor|pre=CURSOR
@since : `strftime("%Y %b %d")^"""

filehead_snippet_after = '@since : `strftime("%Y %b %d")`'

def test_vimscript_filter():
    assert get_parsed_body(filehead_snippet) == filehead_snippet_after

