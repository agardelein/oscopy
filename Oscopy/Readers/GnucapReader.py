""" Read gnucap output files

Gnucap files are ordered by columns, one signal by column.
The first column contains the abscisse values and the remainind the signals
values.
The first line is a comment, with the name of each signal.

The signal name is composed of the probe type v, i, ... and the node name
between parenthesis.
The signal name presented to the user is the one read from the file with the
parenthesis stripped, e.g. v(gs) -> vgs or i(Rd) -> iRd.

Class GnucapReader:
   method:
   readsigs():
      Read the signals from a file to gnucap output format.
"""

import re
from Oscopy.Signal import Signal
from Reader import Reader

class GnucapReader(Reader):
    def readsigs(self):
        """ Read the signals from the file

        First get_ the signal names from the first line, the abscisse
        is the first column
        Then read the values and assign them to the signals.
        Finally, assign the abscisse to each signal.

        The whole file is read at once, instead of reading col by col.
        """
        self.slist = []
        sdict = {}
        try:
            fil = open(self.fn)
        except IOError:
            return {}

        # Get signal names from first line, remove leading "#"
        def f(c): return c != "(" and c != ")" # remove ()
        for names in fil:
            nlist = names.lstrip('#').split()
            break  # Read only the first line

        plist = []
        for name in nlist: # Extract signal names
            u = self.unitfromprobe(name.split('(', 1)[0])
            name = filter(f, name.strip())
            s = Signal(name, self, u)
            self.slist.append(s)
            plist.append([])

        # Read values and assign to signals
        # First put the points into a table of list
        for vals in fil:
            vallist = vals.split()
            for i, v in enumerate(vallist):
                plist[i].append(float(v))
        fil.close()

        # Assign abscisse to signals
        ref = self.slist.pop(0)
        ref.set_data(plist.pop(0))
        for i, s in enumerate(self.slist):
            s.set_ref(ref)
            s.set_data(plist[i])
            sdict[s.get_name()] = s
        return sdict

    def unitfromprobe(self, pn = ""):
        """ Return the unit name (un) from the probe name (pn)
        """
        if pn == "":
            return pn

        # For now only element probe
        uns = {"v":"V", "vout":"V", "vin":"V", "i":"A", "p":"W",\
                   "nv":"", "ev":"", "r":"Ohms", "y":"S",\
                   "Time":"s", "Freq":"Hz"}
        if uns.has_key(pn):
            return uns[pn]
        else:
            return ""

    def detect(self, fn):
        """ Look at the header, if it if something like
        #Name probe(name)
        """
        self.check(fn)
        try:
            f = open(fn)
        except IOError, e:
            return False
        s = f.readline()
        f.close()
        # A better regex which looks at all probe should be better !
        return len(re.findall('^#\w+\s+[\w\(\)]+', s)) > 0
