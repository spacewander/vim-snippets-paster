def make_paster(src, dest):
    """to make creating function in loop possible"""
    return lambda input: paste(src, dest, input)

def paste(src, dest, input):
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
    return '\n'.join(output)

