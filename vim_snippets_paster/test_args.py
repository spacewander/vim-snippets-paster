import pytest

from .main import main

@pytest.fixture()
def snippet():
    return '../snippets/test.snippets'

def test_correct_argv(snippet):
    main(['-f', 'ultisnips', '-t', 'xptemplate', snippet])

def test_wrong_type(snippet):
    with pytest.raises(ValueError):
        main(['-f', 'ultisnips', '-t', 'ultisnips', snippet])

def test_missing_f(snippet):
    with pytest.raises(SystemExit):
        main(['-t', 'ultisnips', snippet])

def test_missing_t(snippet):
    with pytest.raises(SystemExit):
        main(['-f', 'ultisnips', snippet])

def test_missing_snippet():
    with pytest.raises(SystemExit):
        main(['-f', 'ultisnips', '-t', 'xptemplate'])

