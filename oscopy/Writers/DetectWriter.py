""" Automagical detection of Writer to use

DetectWriter(fmt, fn)
Automagically return a Writer to use for file writing

"""
import os.path
from os import access
from Writer import WriteError
from GnucapWriter import GnucapWriter

WRITERS = [GnucapWriter]

def DetectWriter(fmt, fn, ov=False):
    """ Return a writer object
    """
    if not fn:
        raise WriteError("No file specified")
    if os.path.exists(fn):
        if not ov:
            raise WriteError("File does exist")
        elif not os.path.isfile(fn):
            raise WriteError("File is not a file")
        elif not os.access(fn, os.W_OK):
            raise WriteError("Cannot access file")
    for writer in WRITERS:
        w = writer()
        if w.detect(fmt):
            return w
    return None

