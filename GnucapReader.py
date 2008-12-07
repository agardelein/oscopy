""" Read gnucap output files

Gnucap files are ordered by columns, one signal by column.
The first column contains the abscisse values and the remainind the signals
values.
The first line is a comment, with the name of each signal.

The signal name is composed of the probe type v, i, ... and the node name
between parenthesis.
The signal name presented to the user is the one read from the file with the
parenthesis stripped, e.g. v(gs) -> vgs or i(Rd) -> iRd.

Class GnucapRead:
   method:
   getsiglist():
      Read the signals from a file to gnucap output format.
"""

from __future__ import with_statement
from Signal import Signal
from ReaderBase import *

class GnucapReader(ReaderBase):
    # Get signals from first line
    # Abscisse is first read as a signal then assigned to signals
    def getsiglist(self):
        """ Read the signals from the file

        First get the signal names from the first line, the abscisse
        is the first column
        Then read the values and assign them to the signals.
        Finally, assign the abscisse to each signal.

        The whole file is read at once, instead of reading col by col.
        """
        self.slist = []
        sdict = {}
        fil = open(self.fn)

        # Get signal names from first line, remove leading "#"
        def f(c): return c != "(" and c != ")" # remove ()
        for names in fil:
            nlist = names.lstrip('#').split()
            break  # Read only the first line

        for name in nlist: # Extract signal names
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
