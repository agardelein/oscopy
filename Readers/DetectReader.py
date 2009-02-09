""" Automagical detection of file type

Detect(file)
   Automagically select the Reader to use for reading file
"""
import sys
sys.path.insert(0, 'Readers')
import os.path
import Readers
import GnucapReader
import MathReader
import types

rds = ["GnucapReader", "MathReader"]

def DetectReader(fn):
    """ Return a reader object on the file
    """
    if type(fn) != types.StringType:
        return None
    endl = "\n"
    excpt = None
    for rd in rds:
        s = "tmp = " + rd + "." + rd + "()" + endl \
            + "res = tmp.detect(fn)"
        try:
            exec(s)
        except Readers.Reader.ReadError, e:
            excpt = e
            continue
        if res == True:
            return tmp
    if not excpt == None:
        raise excpt
    return None
