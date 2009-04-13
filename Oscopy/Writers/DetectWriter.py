""" Automagical detection of Writer to use

DetectWriter(fmt, fn)
Automagically return a Writer to use for file writing

"""
import os.path
from os import access
from Writer import WriteError
from GnucapWriter import GnucapWriter

wrts = ['GnucapWriter']

def DetectWriter(fmt, fn, ov = False):
    """ Return a writer on the file
    """
    if not isinstance(fmt, str) or not isinstance(fn, str):
        return None
    if not fn:
        raise WriteError("No file specified")
    if os.path.exists(fn):
        if not ov:
            raise WriteError("File does exist")
        elif not os.path.isfile(fn):
            raise WriteError("File is not a file")
        elif not os.access(fn, os.W_OK):
            raise WriteError("Cannot access file")
    endl = "\n"
    for wrt in wrts:
        s = "tmp = %s()\nres = tmp.detect(fmt)" % wrt
        exec(s)
        if res:
            return tmp
    return None
