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

call_snippet_after = """${1:name}( ${VISUAL} )"""

fcomment_snippet = """XPT fcomment
/**
 * @author : `$author^ | `$email^
 */
"""

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

def test_author():
    with pytest.raises(NotImplementFeatureException):
        get_parsed_body(fcomment_snippet)

