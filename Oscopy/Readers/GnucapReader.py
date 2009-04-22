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
   read_sigs():
   Read the signals from a file to gnucap output format.

   unit_from_probe():
   Return the unit of the signal deduced from the probe name

   detect():
   Return true if the file is gnucap format
"""

import re
from Oscopy.Signal import Signal
from Reader import Reader

class GnucapReader(Reader, object):
    def read_sigs(self):
        """ Read the signals from the file

        First get_ the signal names from the first line, the abscisse
        is the first column
        Then read the values and assign them to the signals.
        Finally, assign the abscisse to each signal.

        The whole file is read at once, instead of reading col by col.
        """
        self.sigs = {}
#       sigs = {}
        try:
            fil = open(self.fn)
        except IOError:
            return {}

        # Get signal names from first line, remove leading "#"
        def f(c): return c != "(" and c != ")" # remove ()
        for names in fil:
            nlist = names.lstrip('#').split()
            break  # Read only the first line

        plist = {}
        i_to_name = []
        for name in nlist: # Extract signal names
            u = self.unit_from_probe(name.split('(', 1)[0])
            name = filter(f, name.strip())
            s = Signal(name, u)
            self.sigs[name] = s
            plist[name] = []
            i_to_name.append(name)
            

        # Read values and assign to signals
        # First put the points into a table of list
        for vals in fil:
            vallist = vals.split()
            for i, v in enumerate(vallist):
                plist[i_to_name[i]].append(float(v))
        fil.close()

        # Assign abscisse to signals
        ref = self.sigs.pop(nlist[0])
        ref.data = plist.pop(nlist[0])
        for sn, s in self.sigs.iteritems():
            s.ref = ref
            s.data = plist[sn]
#            sigs[s.name] = s
        return self.sigs

    def unit_from_probe(self, pn=""):
        """ Return the unit name (un) from the probe name (pn)
        In Gnucap format, the header has the format:
        Time|Freq probe(node) probe(node) probe(node)
        The unit is deduced from the probe name as described in the
        gnucap documentation:
        http://www.gnu.org/software/gnucap/gnucap-man-html/gnucap-man046.html
        """
        if not pn:
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
        # A regex which looks at all probe should be better !
        return len(re.findall('^#\w+\s+[\w\(\)]+', s)) > 0
