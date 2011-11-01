""" Automagical detection of file type
"""
import os.path
from reader import ReadError
from gnucap_reader import GnucapReader
from signal_reader import SignalReader
from cazm_reader import CazmReader
from nsout_reader import NsoutReader
from spice2raw_reader import Spice2rawReader
from spice3raw_reader import Spice3rawReader
from hspice_reader import HspiceReader
from touchstone_reader import TouchstoneReader

READERS = [SignalReader, GnucapReader, CazmReader, NsoutReader,
           Spice2rawReader, Spice3rawReader, HspiceReader,
           TouchstoneReader]

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

