from sys import exit
import optparse

from . import converters
from . import pasters
from . import scissors

def exit_with_msg(msg):
    print(msg)
    exit(1)

def main(argv=None):
    p = optparse.OptionParser('%prog [-f xxx -t yyy] snippet')
    p.add_option('-f', dest='src_type', help='specify the given snippet type')
    p.add_option('-t', dest='dest_type', help='specify the output snippet type')
    # <script> -f one -t another snippet
    if argv is None:
        opt, arg = p.parse_args()
    else:
        opt, arg = p.parse_args(argv) # mock for test

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
        snippet = f.read().split('\n')
    res = paste(opt.src_type, opt.dest_type, snippet)
    return res

def paste(src, dest, snippet):
    # snippet is the list of lines of snippet content
    try:
        converter = getattr(converters, 'convert_%s_to_%s' % (src, dest))
    except AttributeError:
        if src == dest:
            msg = "the snippet type of input and output should not be the same"
            raise ValueError(msg)
        raise ValueError("unsupport snippet type detected")

    paster = getattr(pasters, 'paste_%s' % dest)
    output = getattr(scissors, 'cut_%s' % src)(snippet, converter, paster)
    return output

