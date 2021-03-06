

import re
import io
from oscopy import Signal
from .reader import Reader

class GnucapReader(Reader):
    """ Read gnucap output files

Gnucap files are ordered by columns, one signal by column.
The first column contains the abscisse values and the remainind the signals
values.
The first line is a comment, with the name of each signal.

The signal name is composed of the probe type v, i, ... and the node name
between parenthesis.
The signal name presented to the user is the one read from the file with the
parenthesis stripped, e.g. v(gs) -> vgs or i(Rd) -> iRd.
    """
    # A dictionary mapping gnucap probe names to units.
    # For now only element probes.
    PROBE_UNITS = {"v":"V", "vout":"V", "vin":"V", "i":"A", "p":"W",
                   "nv":"", "ev":"", "r":"Ohms", "y":"S",
                   "Time":"s", "Freq":"Hz"}

    def _read_signals(self):
        """ Read the signals from the file

        First get the signal names from the first line, the abscisse
        is the first column.
        Then read the data values, and finally, assign the abscisse and
        data to each signal.

        Parameter
        ---------
        fn: string
        The filename

        Returns
        -------
        Dict of Signals
        The list of Signals read from the file

        Raises
        ------
        ReaderError
        In case of invalid path or unsupported file format
        """
        units = []
        names = []
        signals = []

        with io.open(self._fn, 'r') as f:
            lines = iter(f)

            # read signal names
            first_line = next(lines)
            for x in first_line.lstrip('#').split():
                unit = self._unit_from_probe(x.split('(', 1)[0])
                units.append(unit)
                name = x.replace('(', '').replace(')', '')
                names.append(name)
                signals.append(Signal(name, unit))

            # read values
            data = [[] for x in range(len(names))]
            # optimization: cache the append methods,
            # avoiding one dictionary lookup per line
            append = [x.append for x in data]
            for values in lines:
                for i, val in enumerate(values.split()):
                    append[i](float(val))

        ref = signals[0]
        ref.data = data[0]
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]

        self._signals = dict(list(zip(names[1:], signals[1:])))
        return self._signals

    def _unit_from_probe(self, probe_name):
        """ Return the unit name from the probe name
        In Gnucap format, the header has the format:
        Time|Freq probe(node) probe(node) probe(node)
        The unit is deduced from the probe name as described in the
        gnucap documentation:
        http://www.gnu.org/software/gnucap/gnucap-man-html/gnucap-man046.html

        Parameter
        ---------
        probe_name: string
        the name of the probe found in the file header

        Returns
        -------
        string
        The unit deduced from the probe name.
        """
        return GnucapReader.PROBE_UNITS.get(probe_name, '')

    def detect(self, fn):
        """ Look at the header, if it if something like
        #Name probe(name)

        Parameter
        ---------
        fn: string
        Path to the file to test

        Returns
        -------
        bool
        True if the file can be handled by this reader
        """
        self._check(fn)
        try:
            f = io.open(fn, 'r')
        except IOError as e:
            return False
        s = f.readline()
        f.close()
        # A regex which looks at all probes should be better !
        return len(re.findall('^#\w+\s+[\w\(\)]+', s)) > 0
