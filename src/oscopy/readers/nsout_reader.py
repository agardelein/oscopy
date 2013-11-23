from __future__ import with_statement

import re
import io
from oscopy import Signal
from reader import Reader, ReadError

class NsoutReader(Reader):
    """ Read NanoSim output files

NanoSim output files contain a header with comments lines startings with ';'
where 'NanoSim' or 'output_format' are expected.
Signals are described with .index keyword:
.index name idx type
and the data follows, the independent variable value one single line
and then each dependent variable with its idx value.

Assume the independent variable is 'Time'

For more details see http://www.rvq.fr/linux/gawfmt.php
    """
    _type_to_unit = {'U': 'V', 'I':'A'}
    _instructions = ['voltage_resolution', 'current_resolution',
                     'time_resolution', 'high_threshold',
                     'high_threshold']
    
    def detect(self, fn):
        """ Look at the header if it contains the keyword 'NanoSim'
        or 'output_format'

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
        except IOError, e:
            return False
        s = f.readline()
        found = False
        while s.startswith(';') and not found:
            found = (s.find('NanoSim') > 0) or (s.find('output_format') > 0)
            s = f.readline()
        f.close()
        return found

    def _read_signals(self):
        """ Read the signals from the file

        First read the header containing:
          - Various information on data interpretation
          - Signals description: .index NAME INDEX TYPE
        and then the data:
          ivar_value1
          index1 dvar_value1
          index2 dvar_value2
          ...
          ivar_value2
          index1 dvar_value1
          index2 dvar_value2
          ...
        Various information is stored in self._info.

        Parameter
        ---------
        fn: string
        The filename

        Returns
        -------
        Dict of Signals
        The list of Signals read from the file
        """
        with io.open(self._fn, 'r') as f:
            lines = iter(f)
            signals = {}

            # Header
            h = lines.next()
            while h.startswith(';') or h.startswith('.'):
                x = h.strip('.').split()
                if x[0] in self._instructions:
                    self._info[x[0]] = x[1]
                elif x[0] == 'index':
                    # Use the .index value to identify the signals
                    s = Signal(x[1], self._type_to_unit[x[3]])
                    signals[x[2]] = s
                h = lines.next()

            # Data, cache the append methods
            data = dict(zip(signals.keys(), [[] for x in xrange(len(signals))]))
            append = dict(zip(data.keys(), [x.append for x in data.values()]))
            refdata = []
            if len(h.split()) == 1: refdata.append(float(h))
            for values in lines:
                x = values.split()
                if len(x) == 1:
                    refdata.append(float(x[0]))
                else:
                    append[x[0]](float(x[1]))

        # Putting it altogether, make a dict of signals with names as keys
        ref = Signal('Time', 's')
        ref.data = refdata
        for k, v in data.iteritems():
            signals[k].data = v
            signals[k].ref = ref
        self._signals = dict(zip([x.name for x in signals.itervalues()],
                                 signals.values()))
        return self._signals
