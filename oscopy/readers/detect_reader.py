""" Automagical detection of file type
"""
import os.path
from reader import ReadError
from gnucap_reader import GnucapReader
from signal_reader import SignalReader
from cazm_reader import CazmReader
from nsout_reader import NsoutReader

READERS = [SignalReader, GnucapReader, CazmReader, NsoutReader]

def DetectReader(filename):
    """ Find which Reader can handle the filename
    Parse the list READERS from first element to last one.
    Use the function Reader.detect().
    On sucess, returns a Reader otherwise None

    Parameter
    ---------
    filename: string
    Path to the file to test
    
    Returns
    -------
    r: Reader
    Instanciated Reader able to read filename
    or
    None
    """
    for reader in READERS:
        r = reader()
        if r.detect(filename):
            return r
    return None

