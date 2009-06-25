""" Automagical detection of file type

Detect(file)
   Automagically select the Reader to use for reading file
"""
import os.path
from reader import ReadError
from gnucap_reader import GnucapReader
from math_reader import MathReader

READERS = [MathReader, GnucapReader]

def DetectReader(filename):
    """ Return a reader object
    """
    for reader in READERS:
        r = reader()
        if r.detect(filename):
            return r
    return None

