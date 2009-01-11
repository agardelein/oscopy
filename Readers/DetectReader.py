""" Automagical detection of file type

Detect(file)
   Automagically select the Reader to use for reading file
"""
import sys
sys.path.insert(0, 'Readers')

from GnucapReader import *
from MathReader import *
from types import *

rds = ["GnucapReader", "MathReader"]

def DetectReader(fn):
    """ Return a reader object on the file
    """
    if type(fn) != StringType:
        return None
    a = MathReader()
    endl = "\n"
    for rd in rds:
        s = "tmp = " + rd + "()" + endl \
            + "res = tmp.detect(fn)"
        print "exec : ", s
        exec(s)
        if res == True:
            return tmp
    return None
