from __future__ import with_statement

import itertools
from writer import Writer

class GnucapWriter(Writer):
    """ Class GnucapWriter -- Handle gnucap format export

    Write signals to columns tab separated format used by Gnucap
    Signals should have the same reference
    """

    def __init__(self):
        """ Instanciate the Reader

        Parameter
        ---------
        None

        Returns
        -------
        GnucapWriter
        The object instanciated
        """
        super(GnucapWriter, self).__init__()
        self._prefixes = ['v', 'vout', 'vin', 'i', 'p', 'nv', 'ev', 'r', 'y',
                          'z', 'zraw', 'pd', 'ps', 'f', 'input', 'ioffset_',
                          'ipassive', 'pi', 'pidb', 'pm', 'pmdb', 'pp']
        self._prefixes.sort()
        self._prefixes.reverse()

    def _get_format_name(self):
        """ Return the format name

        Parameter
        ---------
        None

        Returns
        -------
        string
        The format identifier
        """
        return 'gnucap'

    def _format_check(self, sigs):
        """ Check if all signals have the same reference

        Parameter
        ---------
        sigs: dict of Signals
        The Signal list to write

        Returns
        -------
        bool
        True if no issue found to write the Signal list in this format
        """
        if not sigs:
            return False

        ref = sigs.values()[0].ref
        return all(s.ref is ref for s in sigs.itervalues())

    def write_signals(self, sigs):
        """ Write signals to file
        Loop through all the data of each signal to write
        columns line by line.

        Gnucap format is (tab separated):
        #Time|Freq v(x) v(y) v(aa) ...
        1.234   1.234   1.234  1.234
        1.234   1.234   1.234  1.234
        1.234   1.234   1.234  1.234
        ...

        Parameter
        ---------
        sigs: dict of Signals
        The list of Signals to write

        Returns
        -------
        Nothing
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
        """ Convert signal name to gnucap format e.g. vgs -> v(gs)
        Add parenthesis in the signal name to be compatible with gnucap format

        Parameter
        ---------
        name: string
        The name of the Signal to convert

        Returns
        -------
        name: string
        The converted name
        """
        for p in self._prefixes:
            if name.startswith(p):
                return '%s(%s)' % (p, name.replace(p, '', 1))
        return name

