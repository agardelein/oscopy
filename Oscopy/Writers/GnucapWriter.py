from __future__ import with_statement
""" Export signals to Gnucap format

class GnucapWriter -- Handle gnucap format

   _get_fmt_name()
   Return 'gnucap'

   _fmt_check()
   Return True if all signals have the same reference

   write_sigs()
   Write the signals to file

   format_sig_name()
   Convert signal name to gnucap format e.g. vgs -> v(gs)
"""

import itertools
from Writer import Writer

class GnucapWriter(Writer):
    """ Write signals to columns tab separated format used by Gnucap
    Signals should have the same reference
    """

    def __init__(self):
        super(GnucapWriter, self).__init__()
        self._prefixes = ['v', 'vout', 'vin', 'i', 'p', 'nv', 'ev', 'r', 'y',
                          'z', 'zraw', 'pd', 'ps', 'f', 'input', 'ioffset_',
                          'ipassive', 'pi', 'pidb', 'pm', 'pmdb', 'pp']
        self._prefixes.sort()
        self._prefixes.reverse()

    def _get_fmt_name(self):
        """ Return the format name
        """
        return 'gnucap'

    def _fmt_check(self, sigs):
        """ Check if all signals have the same reference
        """
        if not sigs:
            return False

        ref = sigs.values()[0].ref
        return all(s.ref is ref for s in sigs.itervalues())

    def write_sigs(self, sigs):
        """ Write signals to file
        Loop through all the data of each signal to write
        columns line by line.

        Gnucap format is (tab separated):
        #Time|Freq v(x) v(y) v(aa) ...
        1.234   1.234   1.234  1.234
        1.234   1.234   1.234  1.234
        1.234   1.234   1.234  1.234
        ...

        """
        SEPARATOR = '\t'
        # Overwrite file or not
        self._ow = True
        if self._ow:
            mode = "w"
        else:
            mode = "a"

        # construct a list of signals, with the reference signal first
        s = sigs.values()
        s.insert(0, s[0].ref)

        with open(self._fn, mode) as f:
            # write the header
            names = map(self.format_sig_name, map(lambda x: x.name, s))
            f.write('#%s\n' % SEPARATOR.join(names))

            # write the data
            data = (iter(x.data) for x in s)
            for x in itertools.izip(*tuple(data)):
                f.write('%s\n' % SEPARATOR.join(map(str, x)))

    def format_sig_name(self, name):
        """ Add parenthesis in the signal name to be compatible
        with gnucap format
        """
        for p in self._prefixes:
            if name.startswith(p):
                return '%s(%s)' % (p, name.replace(p, '', 1))
        return name

