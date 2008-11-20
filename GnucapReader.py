from __future__ import with_statement
from Signal import Signal
from BaseFileType import *

class GnucapReader(BaseFileType):
    # Get signals from first line
    # Abscisse is first read as a signal then assigned to signals
    def getsiglist(self, fn):
        firstline = 1
        sdict = {}
        slist = []
        fil = open(fn)
        for names in fil:
            if firstline == 1:
                # Get signal names from first line, remove leading "#"
                firstline = 0
                nlist = names.lstrip('#').split()
                for name in nlist:
                    tmp = ""
                    for i in name.strip():
                        if i!='(' and i!= ')': tmp = tmp + i
                    s = Signal(tmp, fn, name)
                    s.pts = []
                    slist.append(s)
            else:
                # Read values and assign to signals
                vallist = names.split()
                for i, v in enumerate(vallist):
                    slist[i].pts.append(v)

        # Assign abscisse to signals
        ref = slist.pop(0)
        for s in slist:
            s.ref = ref
            sdict[s.name] = s
        fil.close()
        return sdict
