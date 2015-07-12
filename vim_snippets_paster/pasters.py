def make_paster(src, dest):
    return lambda converter, texts: paste(src, dest, converter, texts)

def paste(src, dest, converter, texts):
    """
    handle texts in this format:
    [('others', text0), ('snippet', text1), ...]

    Use paste_non_snippets to handle text with 'others' tag,
    use converter to handle text with 'snippet' tag.
    Then paste all results into the final snippet.
    """
    output = []
    ct = {}
    if src in ('snipmate', 'xptemplate'):
        for tag, text in texts:
            if tag == 'others':
                output.append(paste_non_snippets(src, dest, text, ct))
            elif tag == 'snippet':
                output.append(converter(text, ct) + '\n') # for a pretty output
    else:
        for tag, text in texts:
            if tag == 'others':
                output.append(paste_non_snippets(src, dest, text, ct))
            elif tag == 'snippet':
                output.append(converter(text, ct))

    if len(output) == 0:
        return ''

    # if the first part is wrapped with comment, insert the header after it
    if dest == 'snipmate':
        header = 'version 1'
        if len(output[0]) != 0 and output[0][0] == '#':
            return output[0] + '\n' + header + '\n\n' + '\n'.join(output[1:])
        else:
            return header + '\n\n' + '\n'.join(output)
    elif dest == 'xptemplate':
        # don't implement xpt-snippet-mark
        if 'priority' in ct:
            header = ct['priority']
        else:
            header = 'XPTemplate priority=lang'
        if len(output[0]) != 0 and output[0][0] == '"':
            return output[0] + '\n' + header + '\n\n' + '\n'.join(output[1:])
        else:
            return header + '\n\n' + '\n'.join(output)
    else:
        return "\n".join(output)

def paste_non_snippets(src, dest, text, ct):
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
    for line in text:
        line = line.lstrip()
        # simply append all empty lines
        if line == '':
            output.append(line)
        # handle comment
        elif line.startswith(old_comment):
            if new_comment != old_comment:
                # Sometimes there is comment art in the snippet, like:
                # ######################
                # ##  snippet for C   ##
                # ######################
                #
                # Should I convert to something like:
                # """"""""""""""""""""""
                # ""  snippet for C   ""
                # """"""""""""""""""""""
                comment_len = 1
                line_len = len(line)
                while comment_len < line_len and line[comment_len] == old_comment:
                    comment_len += 1
                line = new_comment * comment_len + line[comment_len:]
            output.append(line)
        elif line.startswith('XPTvar'):
            _, name, value = line.split(None, 2)
            ct[name] = value # all XPTvar start with $
        # handle those can be remained in other snippet type
        else:
            if line.startswith('extends '):
                if dest in ('snipmate', 'ultisnips'):
                    output.append(line)
            elif line.startswith('priority ') and dest == 'xptemplate' and \
                    not 'priority' in ct:
                priority = int(line.split(' ', 1)[1].strip())
                ct['priority'] = u_priority_to_xp(priority)
            elif line.startswith('XPTemplate ') and dest == 'ultisnips' and \
                    not 'priority' in ct:
                for pair in line.split():
                    if pair.startswith('priority='):
                        ct['priority'] = True
                        priority = xp_priority_to_u(pair.partition('=')[2])
                        # 0 is default, no need to define
                        if priority != 'priority 0':
                            output.append(priority)
                        break
    output = '\n'.join(output)
    # a little newline is acceptable, but empty content is not
    if output.strip() == '':
        return ''
    return output

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
    The format of xptemplate one is 'priority=lang([+-]%d)', or 'priority=0'

    Ultisnips priority is an integer default to 0. It can be negative.
    For xptemplate priority, see :help xpt-priority-value and
    :help xpt-priority-format.
    """
    if priority > xp_priority_map['lang']:
        return 'XPTemplate priority=0'
    if priority == 0:
        return 'XPTemplate priority=lang'
    elif priority < 0:
        return 'XPTemplate priority=lang+%d' % -priority
    else:
        return 'XPTemplate priority=lang-%d' % priority

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

