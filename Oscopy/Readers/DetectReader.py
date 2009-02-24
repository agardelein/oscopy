""" Automagical detection of file type

Detect(file)
   Automagically select the Reader to use for reading file
"""
import sys
import os.path
import types
from Reader import ReadError
from GnucapReader import GnucapReader
from MathReader import MathReader

rds = ["GnucapReader", "MathReader"]

def DetectReader(fn):
    """ Return a reader object on the file
    """
    if type(fn) != types.StringType:
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
    if not excpt == None:
        raise excpt
    return None
