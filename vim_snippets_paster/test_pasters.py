from .pasters import paste

extends = "extends html, css"

def test_extends():
    lines = [extends]
    assert paste('snipmate', 'ultisnips', lines, {}) == extends
    assert paste('snipmate', 'xptemplate', lines, {}) == ''
    assert paste('ultisnips', 'snipmate', lines, {}) == extends
    assert paste('ultisnips', 'xptemplate', lines, {}) == ''

def test_priority_u():
    priority_u = "priority  1  "
    priority_u2 = "priority 4  "

    lines = [priority_u]
    assert paste('ultisnips', 'snipmate', lines, {}) == ''
    lines = [priority_u2]
    ct = {}
    assert paste('ultisnips', 'xptemplate', lines, ct) == 'XPTemplate priority=12'
    assert ct['has_priority'] == True
    lines = [priority_u, priority_u2]
    assert paste('ultisnips', 'xptemplate', lines, {}) == 'XPTemplate priority=15'

def test_priority_x():
    priority_x = "XPTemplate priority=lang "
    priority_x2 = "XPTemplate priority=32 key=$ "

    lines = [priority_x]
    assert paste('xptemplate', 'snipmate', lines, {}) == ''
    assert paste('xptemplate', 'ultisnips', lines, {}) == ''
    lines = [priority_x2]
    assert paste('xptemplate', 'ultisnips', lines, {}) == 'priority -16'

    priority_x3 = "XPTemplate priority=3"
    priority_x4 = "XPTemplate priority=like+4"
    priority_x5 = "XPTemplate priority=all-"
    priority_x6 = "XPTemplate priority=all-1"

    assert paste('xptemplate', 'ultisnips', [priority_x3], {}) == 'priority 13'
    assert paste('xptemplate', 'ultisnips', [priority_x4], {}) == 'priority -20'
    assert paste('xptemplate', 'ultisnips', [priority_x5], {}) == 'priority -47'
    assert paste('xptemplate', 'ultisnips', [priority_x6], {}) == 'priority -47'

