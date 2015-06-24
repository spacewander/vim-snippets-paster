from .pasters import paste_non_snippets

def test_convert_comment():
    lines = ["# This is a comment"]
    assert paste_non_snippets('ultisnips', 'xptemplate', lines, {}) == \
            '" This is a comment'
    assert paste_non_snippets('xptemplate', 'ultisnips', lines, {}) == ''
    assert paste_non_snippets('snipmate', 'ultisnips', lines, {}) == lines[0]

    lines = ["## This is also a comment"]
    assert paste_non_snippets('ultisnips', 'xptemplate', lines, {}) == \
            '"" This is also a comment'
    lines = ['" Test with more comment']
    assert paste_non_snippets('xptemplate', 'snipmate', lines, {}) == \
            '# Test with more comment'

def test_extends():
    extends = "extends html, css"
    lines = [extends]
    assert paste_non_snippets('snipmate', 'ultisnips', lines, {}) == extends
    assert paste_non_snippets('snipmate', 'xptemplate', lines, {}) == ''
    assert paste_non_snippets('ultisnips', 'snipmate', lines, {}) == extends
    assert paste_non_snippets('ultisnips', 'xptemplate', lines, {}) == ''

def test_priority_u():
    priority_u = "priority  1  "
    priority_u2 = "priority 4  "

    lines = [priority_u]
    assert paste_non_snippets('ultisnips', 'snipmate', lines, {}) == ''
    lines = [priority_u2]
    ct = {}
    paste_non_snippets('ultisnips', 'xptemplate', lines, ct)
    assert ct['priority'] == 'XPTemplate priority=12'
    lines = [priority_u, priority_u2]
    ct = {}
    paste_non_snippets('ultisnips', 'xptemplate', lines, ct)
    assert ct['priority'] == 'XPTemplate priority=15'

def test_priority_x():
    priority_x = "XPTemplate priority=lang "
    priority_x2 = "XPTemplate priority=32 key=$ "

    lines = [priority_x]
    assert paste_non_snippets('xptemplate', 'snipmate', lines, {}) == ''
    assert paste_non_snippets('xptemplate', 'ultisnips', lines, {}) == ''
    lines = [priority_x2]
    assert paste_non_snippets('xptemplate', 'ultisnips', lines, {}) == \
            'priority -16'

    priority_x3 = "XPTemplate priority=3"
    priority_x4 = "XPTemplate priority=like+4"
    priority_x5 = "XPTemplate priority=all-"
    priority_x6 = "XPTemplate priority=all-1"

    assert paste_non_snippets('xptemplate', 'ultisnips', [priority_x3], {}) == \
            'priority 13'
    assert paste_non_snippets('xptemplate', 'ultisnips', [priority_x4], {}) == \
            'priority -20'
    assert paste_non_snippets('xptemplate', 'ultisnips', [priority_x5], {}) == \
            'priority -47'
    assert paste_non_snippets('xptemplate', 'ultisnips', [priority_x6], {}) == \
            'priority -47'

