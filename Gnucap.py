from __future__ import with_statement
from Signal import Signal
import os.path
from ExceptErrors import *

class Gnucap:
    # Get signals from line
    def getsiglist(self, names, f):
        slist = []
        nlist = names.split()
        domain = nlist.pop(0)
        for name in nlist:
            s = Signal()
            s.domain = domain
            s.origfile = f
            # Original signal name
            s.origname = name
            # Signal name
            s.name = ""
            # Remove parenthesis from name
            for i in name.strip():
                if i!='(' and i!= ')': s.name = s.name + i
            slist.append(s)
        return slist
            
    # Read the variable list from file
    def loadfile(self, fi):
        if fi == "":
            raise LoadFileError("No file specified")
        if not os.path.exists(fi):
            raise LoadFileError("File do not exist")
        if not os.path.isfile(fi):
            raise LoadFileError("File is not a file")

        with open(fi) as f:
            s = f.readline()
            s = s.lstrip('#')
        return self.getsiglist(s, file)
