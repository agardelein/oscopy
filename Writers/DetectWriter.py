""" Automagical detection of Writer to use

DetectWriter(fmt, fn)
Automagically return a Writer to use for file writing

"""
import sys
import types
import Writers.Writer
import Writers.GnucapWriter
import os.path

wrts = ['GnucapWriter']

def DetectWriter(fmt, fn, ov = False):
    """ Return a writer on the file
    """
    if type(fmt) != types.StringType or type(fn) != types.StringType:
        return None
    if fn == "":
        raise Writers.Writer.WriteError("No file specified")
    if os.path.exists(fn):
        if ov == False:
            raise Writers.Writer.WriteError("File does exist")
        elif not os.path.isfile(fn):
            raise Writers.Writer.WriteError("File is not a file")

    endl = "\n"
    for wrt in wrts:
        s = "tmp = Writers." + wrt + "." + wrt + "()" + endl \
            + "res = tmp.detect(fmt)"
        exec(s)
        if res == True:
            return tmp
    return None
