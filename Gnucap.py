from __future__ import with_statement
from Signal import Signal

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
        if file == "":
            print "load: no file specified"
            return False
        with open(fi) as f:
            s = f.readline()
            s = s.lstrip('#')
        return self.getsiglist(s, file)
