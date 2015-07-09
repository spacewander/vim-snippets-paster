import difflib
import os.path

from .main import paste

snippte_dir = os.path.dirname(os.path.abspath(__file__))
snippte_dir = os.path.join(os.path.split(snippte_dir)[0], 'snippets')

def assert_snippet_equal(from_type, to_type):
    with open(os.path.join(snippte_dir, 'in.%s' % from_type)) as f:
        from_snippet = f.read().splitlines()
    snippet = paste(from_type, to_type, from_snippet)
    with open(os.path.join(snippte_dir, 'out_%s.%s' % (from_type, to_type))) as f:
        to_snippet = f.read().rstrip()
    if snippet != to_snippet:
        print('out_%s.%s changed' % (from_type, to_type))
        print('\n'.join(difflib.unified_diff(to_snippet.splitlines(),
            snippet.splitlines())))
        assert False
    else:
        assert True

def test_snipmate2ultisnips():
    assert_snippet_equal('snipmate', 'ultisnips')

def test_ultisnips2snipmate():
    assert_snippet_equal('ultisnips', 'snipmate')

def test_xptemplate2snipmate():
    assert_snippet_equal('xptemplate', 'snipmate')

def test_xptemplate2ultisnips():
    assert_snippet_equal('xptemplate', 'ultisnips')

