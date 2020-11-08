    ##############
    # FORMATTING #
    ##############

## mIRC colour codes
#
# Number 	Name
# 00 	    white
# 01 	    black
# 02 	    blue (navy)
# 03 	    green
# 04 	    red
# 05 	    brown (maroon)
# 06 	    purple
# 07 	    orange (olive)
# 08 	    yellow
# 09 	    light green (lime)
# 10 	    teal (a green/blue cyan)
# 11 	    light cyan (cyan / aqua)
# 12 	    light blue (royal)
# 13 	    pink (light purple / fuchsia)
# 14 	    grey/gray
# 15 	    light grey/gray (silver)

import re

def white(s):
    """Returns a white string."""
    return '\x0300%s\x03' % s

def black(s):
    """Returns a black string."""
    return '\x0301%s\x03' % s

def blue(s):
    """Returns a blue string."""
    return '\x0302%s\x03' % s

def green(s):
    """Returns a green string."""
    return '\x0303%s\x03' % s
    
def red(s):
    """Returns a red string."""
    return '\x0304%s\x03' % s

def brown(s):
    """Returns a brown string."""
    return '\x0305%s\x03' % s

def purple(s):
    """Returns a purple string."""
    return '\x0306%s\x03' % s

def orange(s):
    """Returns a orange string."""
    return '\x0307%s\x03' % s

def yellow(s):
    """Returns a yellow string."""
    return '\x0308%s\x03' % s

def light_green(s):
    """Returns a light green string."""
    return '\x0309%s\x03' % s

def teal(s):
    """Returns a teal string."""
    return '\x0310%s\x03' % s

def light_blue(s):
    """Returns a teal string."""
    return '\x0311%s\x03' % s

def dark_blue(s):
    """Returns a dark blue string."""
    return '\x0312%s\x03' % s

def pink(s):
    """Returns a pink string."""
    return '\x0313%s\x03' % s

def dark_grey(s):
    """Returns a dark grey string."""
    return '\x0314%s\x03' % s

def dark_gray(s):
    """Returns a dark grey string."""
    return '\x0314%s\x03' % s

def light_grey(s):
    """Returns a light gray string."""
    return '\x0315%s\x03' % s

def light_gray(s):
    """Returns a light gray string."""
    return '\x0315%s\x03' % s

def bold(s):
    """Returns the string s, bolded."""
    return '\x02%s\x02' % s

def nobold(s):
    """Returns the string s, with bold removed."""
    return s.replace('\x02', '')

def underline(s):
    """Returns the string s, underlined."""
    return '\x1F%s\x1F' % s

def italic(s):
    """Returns the string s, italicised."""
    return '\x1D%s\x1D' % s

def reverse(s):
    """Returns the string s, reverse-videoed."""
    return '\x16%s\x16' % s

def stripBold(s):
    """Returns the string s, with bold removed."""
    return s.replace('\x02', '')

def stripItalic(s):
    """Returns the string s, with italics removed."""
    return s.replace('\x1d', '')

_stripColorRe = re.compile(r'\x03(?:\d{1,2},\d{1,2}|\d{1,2}|,\d{1,2}|)')
def stripColor(s):
    """Returns the string s, with color removed."""
    return _stripColorRe.sub('', s)

def stripReverse(s):
    """Returns the string s, with reverse-video removed."""
    return s.replace('\x16', '')

def stripUnderline(s):
    """Returns the string s, with underlining removed."""
    return s.replace('\x1f', '').replace('\x1F', '')

def stripFormatting(s):
    """Returns the string s, with all formatting removed."""
    s = stripColor(s)
    s = stripBold(s)
    s = stripReverse(s)
    s = stripUnderline(s)
    s = stripItalic(s)
    return s.replace('\x0f', '').replace('\x0F', '')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: