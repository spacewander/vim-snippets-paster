# open snippets in ../snippets to understand snippet syntax of each plugin

def cut_snipmate(snippet, convert, paste):
    return convert(snippet)

def cut_ultisnips(snippet, convert, paste):
    return ""

def cut_xptemplate(snippet, convert, paste):
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
    def comment(line):
        if line.strip() != '':
            return '"' + line
        return line

    in_snip = False
    begin = end = last_nonempty_line = 0
    texts = []
    for linum, line in enumerate(snippet):
        if in_snip is False and line.startswith('XPT '):
            end = linum
            in_snip = True
            # cut non-snippet text
            texts.append('\n'.join(map(comment, snippet[begin:end])))
            begin = end
        elif in_snip is True:
            if line.startswith('..XPT'):
                in_snip = False
                end = linum
                texts.append(convert(snippet[begin:end])) # cut snippet text
                begin = end + 1
            elif line.startswith('XPT '):
                texts.append(convert(snippet[begin:last_nonempty_line+1]))
                begin = end = linum
            elif line != '':
                last_nonempty_line = linum

    if in_snip is True:
        texts.append(convert(snippet[begin:last_nonempty_line+1]))
    else:
        texts.append('\n'.join(map(comment, snippet[begin:])))
    return paste(texts)

