""" Automagical detection of file type

Detect(file)
   Automagically select the Reader to use for reading file
"""
import os.path
from Reader import ReadError
from GnucapReader import GnucapReader
from MathReader import MathReader

READERS = [GnucapReader, MathReader]

def DetectReader(filename):
    """ Return a reader object
    """
    for reader in READERS:
        r = reader()
        try:
            if r.detect(filename):
                return r
        except ReadError:
            pass
    return None

