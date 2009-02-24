""" Automagical detection of Writer to use

DetectWriter(fmt, fn)
Automagically return a Writer to use for file writing

"""
import sys
import types
import os.path
from os import access
from Writer import WriteError
from GnucapWriter import GnucapWriter

wrts = ['GnucapWriter']

def DetectWriter(fmt, fn, ov = False):
    """ Return a writer on the file
    """
    if type(fmt) != types.StringType or type(fn) != types.StringType:
        return None
    if fn == "":
        raise WriteError("No file specified")
    if os.path.exists(fn):
        if ov == False:
            raise WriteError("File does exist")
        elif not os.path.isfile(fn):
            raise WriteError("File is not a file")
        elif not os.access(fn, os.W_OK):
            raise WriteError("Cannot access file")
    endl = "\n"
    for wrt in wrts:
        s = "tmp = " + wrt + "()" + endl \
            + "res = tmp.detect(fmt)"
        exec(s)
        if res == True:
            return tmp
    return None
