from sys import exit
import optparse

import converters
import pasters
import scissors

def exit_with_msg(msg):
    print(msg)
    exit(1)

def main():
    p = optparse.OptionParser('%prog [-f xxx -t yyy] snippet')
    p.add_option('-f', dest='src_type', help='specify the given snippet type')
    p.add_option('-t', dest='dest_type', help='specify the output snippet type')
    # <script> -f one -t another snippet
    opt, arg = p.parse_args()
    if len(arg) != 1:
        if len(arg) > 1:
            exit_with_msg('can only convert a snippet at a time')
        else:
            exit_with_msg('miss snippet')
    if opt.src_type is None:
        exit_with_msg('miss given snippet type')
    if opt.dest_type is None:
        exit_with_msg('miss output snippet type')

    with open(arg[0]) as f:
        snippet = f.read()
    res = paste(opt.src_type, opt.dest_type, snippet)
    print(res)

def paste(src, dest, snippet):
    try:
        converter = getattr(converters, 'convert_%s_to_%s' % (src, dest))
    except AttributeError:
        if src == dest:
            msg = "the snippet type of input and output should not be the same"
            raise ValueError(msg)
        raise ValueError("unsupport snippet type detected")

    paster = (pasters, 'paste_%s' % dest)
    output = getattr(scissors, 'cut_%s' % src)(snippet, converter, paster)
    return output

