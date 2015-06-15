import os.path

from .main import paste

snippte_dir = os.path.dirname(os.path.abspath(__file__))
snippte_dir = os.path.join(os.path.split(snippte_dir)[0], 'snippets')

def test_snipmate2ultisnips():
    with open(os.path.join(snippte_dir, 'in.snipmate')) as f:
        snipmate_snippet = f.read().splitlines()
    snippet = paste('snipmate', 'ultisnips', snipmate_snippet)
    with open(os.path.join(snippte_dir, 'out_snipmate.ultisnips')) as f:
        ultisnips_snippet = f.read().rstrip()
    assert snippet == ultisnips_snippet

