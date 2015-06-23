from . import convert
from .snippet import Snippet
from .ultility import (NotImplementFeatureException, UnsupportFeatureException,
                       format_placeholders)

def test_not_implement_feature_exception():
    try:
        raise NotImplementFeatureException("some")
    except NotImplementFeatureException as e:
        assert e.message == 'some'
    try :
        raise NotImplementFeatureException(feature="some")
    except NotImplementFeatureException as e:
        assert e.message == '%s is not implemented' % 'some'

def test_unsupport_feature_exception():
    try :
        raise UnsupportFeatureException("some")
    except UnsupportFeatureException as e:
        assert e.message == 'some'
    try :
        raise UnsupportFeatureException(feature="some")
    except UnsupportFeatureException as e:
        assert e.message == '%s is unsupport' % 'some'

def test_format_placeholders():
    lines = ["it is ${VISUAL}", 'and ${0}']
    assert format_placeholders(lines) == ["it is $VISUAL", 'and $0']

def test_not_implement_handle():
    lines = """snippet st struct
        struct ${1:`vim_snippets#Filename('$1_t', 'name')`} {
            ${2:/* data */}
        }${3: /* optional variable list */};
    }""".splitlines()
    warning = convert('snipmate', 'xptemplate', lines, {}).splitlines()
    assert len(warning) == 6
    # header should report that feature is not implemented
    assert warning[0].endswith('is not implemented')
    assert warning[1][0] == '"' # and comment out the whole input

def test_unsupport_handle():
    lines = """snippet "white space"
endsnippet""".splitlines()
    warning = convert('ultisnips', 'xptemplate', lines, {}).splitlines()
    assert warning == ([
    '"xptemplate doesn\'t allow whitespace in snippet trigger',
    '"snippet "white space"',
    '"endsnippet'])

