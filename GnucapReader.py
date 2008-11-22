from __future__ import with_statement
from Signal import Signal
from ReaderBase import *

class GnucapReader(ReaderBase):
    # Get signals from first line
    # Abscisse is first read as a signal then assigned to signals
    def getsiglist(self):
        self.slist = []
        sdict = {}
        fil = open(self.fn)

        # Get signal names from first line, remove leading "#"
        def f(c): return c != "(" and c != ")" # remove ()
        for names in fil:
            nlist = names.lstrip('#').split()
            break

        for name in nlist:
            name = filter(f, name.strip())
            s = Signal(name, self)
            self.slist.append(s)

        # Read values and assign to signals
        for names in fil:
            vallist = names.split()
            for i, v in enumerate(vallist):
                self.slist[i].pts.append(v)
        fil.close()

        # Assign abscisse to signals
        ref = self.slist.pop(0)
        for s in self.slist:
            s.ref = ref
            sdict[s.name] = s
        return sdict
