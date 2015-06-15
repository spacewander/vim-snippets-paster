def make_paster(src, dest):
    """to make creating function in loop possible"""
    return lambda input, ct: paste(src, dest, input, ct)

def paste(src, dest, input, ct):
    """
    paste non-snippets contents.

    Remain all the comments.
    As for features:
    snipmate:
        * version(removed)
        * extends(remained in ultisnips)
    ultisnips:
        * extends(remained in snipmate)
        * priority(remained in xptemplate)
        * clearsnippets(removed)
        * global(removed, it isn't support by snippet part yet)
    xptemplate:
        * xpt-snippet-header(remained in ultisnips)
        * XPTinclude(removed)
        * xpt-snippet-function(unsupport, just comment it)
    """
    if src in 'xptemplate':
        old_comment = '"'
    else:
        old_comment = '#'
    if dest in 'xptemplate':
        new_comment = '"'
    else:
        new_comment = '#'

    output = []
    for line in input:
        line = line.lstrip()
        if line.startswith(old_comment):
            if new_comment != old_comment:
                line[0] = new_comment
            output.append(line)
        elif line == '':
            output.append(line)
        else:
            if line.startswith('extends '):
                if dest in ('snipmate', 'ultisnips'):
                    output.append(line)
            elif line.startswith('priority ') and dest == 'xptemplate' and \
                    not 'has_priority' in ct:
                ct['has_priority'] = True
                priority = int(line.split(' ', 1)[1].strip())
                output.append(u_priority_to_xp(priority))
            elif line.startswith('XPTemplate ') and dest == 'ultisnips' and \
                    not 'has_priority' in ct:
                for pair in line.split():
                    if pair.startswith('priority='):
                        ct['has_priority'] = True
                        priority = xp_priority_to_u(pair.partition('=')[2])
                        # 0 is default, no need to define
                        if priority != 'priority 0':
                            output.append(priority)
                        break

    return '\n'.join(output)


xp_priority_map = {
    'all'		: 64,
    'spec'		: 48,
    'like'		: 32,
    'lang'		: 16,
    'sub'		: 8,
    'personal'	: 0
}

def u_priority_to_xp(priority):
    """
    Convert ultisnips' priority to xptemplate one.

    Ultisnips priority is an integer default to 0. It can be negative.
    For xptemplate priority, see :help xpt-priority-value and
    :help xpt-priority-format.
    """
    if priority == 0:
        return 'XPTemplate priority=lang'
    xp_priority = xp_priority_map['lang'] - priority
    if xp_priority < 0:
        xp_priority = 0
    return 'XPTemplate priority=%d' % xp_priority

def xp_priority_to_u(priority):
    """
    Convert ultisnips' priority to xptemplate one.

    Ultisnips priority is an integer default to 0. It can be negative.
    For xptemplate priority, see :help xpt-priority-value and
    :help xpt-priority-format.
    """
    u_priority = xp_priority_map['lang']
    if '+' in priority:
        priority, _, offset = priority.partition('+')
        if offset == '':
            offset = 1
        else:
            offset = int(offset)
        if priority.isdigit():
            u_priority -= int(priority) + offset
        else:
            u_priority -= xp_priority_map[priority] + offset
    elif '-' in priority:
        priority, _, offset = priority.partition('-')
        if offset == '':
            offset = 1
        else:
            offset = int(offset)
        if priority.isdigit():
            u_priority -= int(priority) - offset
        else:
            u_priority -= xp_priority_map[priority] - offset
    else:
        if priority.isdigit():
            u_priority -= int(priority)
        else:
            u_priority -= xp_priority_map[priority]

    return 'priority %d' % u_priority

