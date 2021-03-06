import pytest

from .snippet import Snippet
from .ultility import NotImplementFeatureException, UnsupportFeatureException
from .xptemplate import parse, build, XptemplateBuilder

def get_parsed_body(input):
    return parse(input.split('\n'), {})[0].body

if_snippet = """XPT if
if`$SPcmd^(`$SParg^`condition^`$SParg^)`$BRif^{
    `cursor^
}"""

if_snippet_after = """if ( ${1:condition} ) {
    ${0}
}"""

def test_normal_snippet():
    assert get_parsed_body(if_snippet) == if_snippet_after

for_snippet = """XPT for hint=for\ (..;..;++)
for (`i^ = `0^; `i^ < `len^; ++`i^) {
    `cursor^
}"""

for_snippet_after = """for (${1:i} = ${2:0}; $1 < ${3:len}; ++$1) {
    ${0}
}"""

def test_mirror():
    assert get_parsed_body(for_snippet) == for_snippet_after

ComeFirst_snippet = """XPT for
XSET ComeFirst=0 len
for (`i^ = `0^; `i^ < `len^; ++`i^)"""

ComeFirst_snippet_after = """for (${3:i} = ${1:0}; $3 < ${2:len}; ++$3)"""

def test_ComeFirst():
    assert get_parsed_body(ComeFirst_snippet) == ComeFirst_snippet_after

ComeLast_snippet = """XPT for
XSET ComeLast=i len
for (`i^ = `0^; `i^ < `len^; ++`i^)"""

ComeLast_snippet_after = """for (${2:i} = ${1:0}; $2 < ${3:len}; ++$2)"""

def test_ComeLast():
    assert get_parsed_body(ComeLast_snippet) == ComeLast_snippet_after

# filter placeholder-edge out
edge_snippet = """XPT edge
`(`XPT`)^"""
edge_snippet1 = """XPT edge
`(`XPT`)^...XPT^"""
edge_snippet2 = """XPT edge
`$SParg `XPT`$SParg^"""

left_only_edge_snippet = """XPT edge
`(`XPT^)"""
left_only_edge_snippet1 = """XPT edge
`(`XPT^...XPT^)"""
left_only_edge_snippet2 = """XPT edge
`$SParg`XPT^"""

def test_edge():
    assert get_parsed_body(edge_snippet) == "(${1:XPT})"
    assert get_parsed_body(edge_snippet1) == "(${1:...XPT})"
    assert get_parsed_body(edge_snippet2) == "  ${1:XPT} "

def test_left_only_edge():
    assert get_parsed_body(left_only_edge_snippet) == "(${1:XPT})"
    assert get_parsed_body(left_only_edge_snippet1) == "(${1:...XPT})"
    assert get_parsed_body(left_only_edge_snippet2) == " ${1:XPT}"

# leading-placeholder define the first placeholder among the same item
leading_placeholder_snippet = """XPT leading
for (`i^ = `0^; `i^ < ``0^; ++`i^)"""

leading_placeholder_snippet_after = """for (${1:i} = $2; $1 < ${2:0}; ++$1)"""

def test_leading_placeholder():
    assert get_parsed_body(leading_placeholder_snippet) == \
            leading_placeholder_snippet_after

memset_snippet = """XPT memset " memset (..., ..., sizeof (...) ... )
memset(`$SParg^`buffer^,`$SPop^`what^0^,`$SPop^sizeof(`$SParg^`type^int^`$SParg^)`$SPop^*`$SPop^`count^`$SParg^)
"""

memset_snippet_after = """memset( ${1:buffer}, ${2:0}, sizeof( ${3:int} ) * ${4:count} )
"""

memset_snippet_defined = """memset(${1:buffer}, ${2:0}, sizeof(${3:int}) * ${4:count})
"""

def test_placeholder():
    assert get_parsed_body(memset_snippet) == memset_snippet_after
    ct = {
        '$SParg': '',
        'some': 'else'
    }
    assert parse(memset_snippet.split('\n'), ct)[0].body == \
            memset_snippet_defined

call_snippet = """XPT call wraponly=param " ..( .. )
`name^(`$SParg^`param^`$SParg^)"""

call_snippet_wraponly = """XPT call wraponly=param " ..( .. )
`name^(`$SParg^`param^`$SParg^)"""

call_snippet_after = """${1:name}( $VISUAL )"""

def test_wrap():
    assert get_parsed_body(call_snippet) == call_snippet_after

def test_wraponly():
    assert get_parsed_body(call_snippet_wraponly) == call_snippet_after

fcomment_snippet = """XPT fcomment
/**
 * @author : `$author^ | `$email^
 */
"""

fcomment_snippet_after = """/**
 * @author : `$author` | `$email`
 */
"""

def test_author():
    assert get_parsed_body(fcomment_snippet) == fcomment_snippet_after

alias_snippet = """XPT fr alias=for hint=for\ (..;..;++)
for (`i^ = `0^; `i^ < `len^; ++`i^) {
    `cursor^
}"""

synonym_snippet = """XPT fr synonym=for|fri hint=for\ (..;..;++)
for (`i^ = `0^; `i^ < `len^; ++`i^) {
    `cursor^
}"""

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

unescape_snippet = """XPT test " \$\(\ bla
test"""

unescape_hint_snippet = """XPT test hint=\$\(\ bla
test"""

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
@since : `strftime("%Y %b %d")^"""

filehead_snippet_after = '@since : `strftime("%Y %b %d")`'

def test_vimscript_filter():
    assert get_parsed_body(filehead_snippet) == filehead_snippet_after

if_snippet_obj = Snippet('ultisnips', name='if',
                    body='if ...', description='if snippet')

if_snippet_obj_after = """XPT if "if snippet
if ...
...XPT"""

XSET_snippet = """XPT XSET
XSET symbol|post=UpperCase(V())
#ifndef `symbol^"""

def test_handle_XSET():
    with pytest.raises(NotImplementFeatureException):
        get_parsed_body(XSET_snippet)

repeation_snippet = """XPT repeation
switch (`^) {
    `...^
    case `^0^ :
        `^
    break;
    `...^"""
repeation_snippet_after = """switch (`^) {
    case `^0^ :
        `^
    break;"""

def test_repeation():
    assert get_parsed_body(repeation_snippet) == repeation_snippet_after

escape_snippet = """XPT escape
`${}^"""

def test_escape_xptemplate_placeholder():
    assert get_parsed_body(escape_snippet) == "${1:\$\{\}}"

## features in building step

def test_build():
    assert build(if_snippet_obj) == if_snippet_obj_after

def get_built_body(snippet):
    return "\n".join(build(snippet).splitlines()[1:-1])

def test_convert_author_and_email():
    user_snippet_obj = Snippet('ultisnips', name='user',
                            body='`$author`\'s `$email`')
    assert get_built_body(user_snippet_obj) == '`$author^\'s `$email^'

def test_convert_viml_code():
    viml_snippet_obj = Snippet('ultisnips', name='viml', body='`echom`')
    assert get_built_body(viml_snippet_obj) == '`echom^'

def wrap_body_to_object(snippet_body):
    return Snippet('ultisnips', name='some', body=snippet_body)

escape_body = "${1:`some^}"
def test_escape_snippet_placeholder():
    builder = XptemplateBuilder(wrap_body_to_object(escape_body))
    assert builder.body == "`\`some\^^"

placeholders = """${1:some} ${1} ${2} ${0:one} ${3} ${4}${VISUAL:else}"""
placeholders2 = """$1 ${1:some} ${2} ${0} ${VISUAL}"""
placeholders3 = """$2 $1 ${1:some} ${3:else}"""
placeholders4 = """$2 $1"""

def test_convert_placeholders():
    builder = XptemplateBuilder(wrap_body_to_object(placeholders))
    assert builder.hasWrap
    assert builder.wrap == 'else'
    assert builder.body == "`some^ `some^ `^ `cursor^ `^ `^`else^"

    builder = XptemplateBuilder(wrap_body_to_object(placeholders2))
    assert builder.hasWrap
    assert builder.wrap == 'VISUAL'
    assert builder.body == "`some^ ``some^ `^ `cursor^ `VISUAL^"

    builder = XptemplateBuilder(wrap_body_to_object(placeholders3))
    assert not builder.hasWrap
    assert builder.body == """XSET ComeFirst=some i else
`i^ `some^ ``some^ `else^"""

    builder = XptemplateBuilder(wrap_body_to_object(placeholders4))
    assert builder.body == """XSET ComeFirst=j i
`i^ `j^"""

nested = """for (${1:i} = ${2:0}; ${3:$1 < 10}; $1${4:++}) """
nested2 = """for (${1:i} = ${2:0}; ${3:${1} < 10}; ${1}${4:++}) """

def test_nested_body():
    with pytest.raises(UnsupportFeatureException):
        XptemplateBuilder(wrap_body_to_object(nested))
    with pytest.raises(UnsupportFeatureException):
        XptemplateBuilder(wrap_body_to_object(nested2))

