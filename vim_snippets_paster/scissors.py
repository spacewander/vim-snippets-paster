# open snippets in ../snippets to understand snippet syntax of each plugin

import re

def make_cutter(src):
    """
    All cutter cut the snippet text and return result like this format:
    [('others', text0), ('snippet', text1), ...]
    """
    return globals()['cut_%s' % src]

def cut_snipmate(snippet):
    """
    file format:
        [version digits]
        [extends filetype]
        snippet[!] xxx
            snippet body
        snippet[!] xxx
            snippet body
    """
    in_snip = False
    begin = end = 0
    texts = []
    begin_without_indent = re.compile('^\S')
    for linum, line in enumerate(snippet):
        if in_snip is False and line.startswith('snippet'):
            end = linum
            in_snip = True
            # cut non-snippet text
            texts.append(('others', snippet[begin:end]))
            begin = end
        elif in_snip is True and re.match(begin_without_indent, line):
            end = linum
            if line.startswith('snippet'):
                # cut snippet text
                texts.append(('snippet', snippet[begin:end]))
            else:
                in_snip = False
                # cut snippet text
                texts.append(('snippet', snippet[begin:end]))
            begin = end

    if in_snip is True:
        texts.append(('snippet', snippet[begin:]))
    else:
        texts.append(('others', snippet[begin:]))
    return texts

def cut_ultisnips(snippet):
    """
    file format:
        [extends filetype]   # extend snippets from filetype x
        [priority digits]   # set priority for all snippets after it

        snippet ...
        endsnippet
    """
    in_snip = False
    begin = end = 0
    texts = []
    for linum, line in enumerate(snippet):
        if in_snip is False and line.startswith('snippet'):
            end = linum
            in_snip = True
            # cut non-snippet text
            texts.append(('others', snippet[begin:end]))
            begin = end
        elif in_snip is True and line.startswith('endsnippet'):
            end = linum
            in_snip = False
            # cut snippet text
            texts.append(('snippet', snippet[begin:end+1]))
            begin = end + 1

    if in_snip is False:
        texts.append(('others', snippet[begin:]))
    return texts

def cut_xptemplate(snippet):
    """
    file format:
        XPTemplate priority=lang keyword=$      | |xpt-snippet-header|

        let s:f = XPTfuncs()                    | |xpt-snippet-function|

        XPTvar $TRUE          true              | |xpt-snippet-variable|
        XPTvar $FALSE         false             |
        XPTvar $NULL          null              |
        XPTvar $UNDEFINED     undefined         |
                                                |
        XPTvar $CL  /*                          |
        XPTvar $CM   *                          |
        XPTvar $CR   */                         |
                                                |

        XPTinclude                              | |xpt-snippet-XPTinclude|
              \ _common/common                  |
              \ _comment/doubleSign             |
              \ _condition/c.like               |

        fun! s:f.js_filename()                  | |xpt-snippet-function|
                return expand( "%" )            |
        endfunction                             |


        XPT cmt hint=/**\ @auth...\ */          | |xpt-snippet|
        XSET author=$author                     | |xpt-snippet-XSET|
        XSET email=$email                       | |xpt-snippet-XSET|
        /**                                     |\
        * @author : `author^ | `email^          | \
        * @description                          |  +|xpt-snippet-body|
        *     `cursor^                          | /
        * @return {`Object^} `desc^             |/
        */
    """
    in_snip = False
    begin = end = last_nonempty_line = 0
    texts = []
    for linum, line in enumerate(snippet):
        if in_snip is False and line.startswith('XPT '):
            end = linum
            in_snip = True
            # cut non-snippet text
            texts.append(('others', snippet[begin:end]))
            begin = end
        elif in_snip is True:
            if line.startswith('..XPT'):
                in_snip = False
                end = linum
                texts.append(('snippet', snippet[begin:end])) # cut snippet text
                begin = end + 1
            elif line.startswith('XPT '):
                texts.append(('snippet', snippet[begin:last_nonempty_line+1]))
                begin = end = linum
            elif line != '':
                last_nonempty_line = linum

    if in_snip is True:
        texts.append(('snippet', snippet[begin:last_nonempty_line+1]))
    else:
        texts.append(('others', snippet[begin:]))
    return texts

