from __future__ import with_statement
from Signal import Signal
from BaseFileType import *

class Gnucap(BaseFileType):
    # Get signals from line
    def getsiglist(self, f):
        
        with open(f) as fil:
            names = fil.readline()
        names = names.lstrip('#')

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

