""" Automagical detection of file type

Detect(file)
   Automagically select the Reader to use for reading file
"""
import os.path
from Reader import ReadError
from GnucapReader import GnucapReader
from MathReader import MathReader

rds = ["GnucapReader", "MathReader"]

def DetectReader(fn):
    """ Return a reader object on the file
    """
    if not isinstance(fn, str):
        return None
    endl = "\n"
    excpt = None
    for rd in rds:
        s = "tmp = " + rd + "()" + endl \
            + "res = tmp.detect(fn)"
        try:
            exec(s)
        except ReadError, e:
            excpt = e
            continue
        if res == True:
            return tmp
    if excpt is not None:
        raise excpt
    return None
