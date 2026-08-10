"""Display Hebrew in widgets that have no bidi support.

tkinter lays every string out left to right, so Hebrew arrives mirrored. The
usual workaround is to reverse the string before handing it over.
"""
import re

# A Hebrew letter, then anything that belongs to the same phrase: more Hebrew,
# spaces, digits, and the punctuation used in compound place names. Keeping
# "; " inside the run matters -- reversing "רצועת עזה" and "ג'באליה" separately
# would show the sub-place before the place it belongs to.
RUN = re.compile(r'[֐-׿][֐-׿0-9\'"״׳’\-;, ]*')
ATOM = re.compile(r'[0-9A-Za-z]+|.')


def rtl(text):
    """Reverse the Hebrew in `text`, leaving any English around it readable.

    Digit and Latin runs keep their own order, so "כיסופים; 21 א" does not come
    back as "12".
    """
    return RUN.sub(lambda m: ''.join(reversed(ATOM.findall(m.group()))), text)
