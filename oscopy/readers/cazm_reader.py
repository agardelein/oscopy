from __future__ import with_statement

import re
from oscopy import Signal
from reader import Reader, ReadError

class CazmReader(Reader):
    _CAZM_ID_STRING = '* CAZM-format output'
    _names_to_units = {'Time': 's', 'time': 's'}
    
    def detect(self, fn):
        self._check(fn)
        try:
            f = open(fn)
        except IOError, e:
            return False
        s = f.readline()
        f.close()
        return s.startswith(self._CAZM_ID_STRING)

    def _read_signals(self):
        units = []
        names = []
        signals = []

        with open(self._fn) as f:
            lines = iter(f)

            # read signal names
            if not lines.next().startswith(self._CAZM_ID_STRING):
                raise ReadError('File is not CAZM format')
            lines.next() # Blank line
            self._info['Analysis type'] = lines.next()
            
            first_line = lines.next()
            for x in first_line.split():
                name = x
                names.append(name)
                # Absolute Unit (a.u.) if no unit found
                # this avoid confusion when calling Graph.set_unit()
                unit = self._names_to_units.get(name, 'a.u.')
                units.append(unit)
                signals.append(Signal(name, unit))

            # read values
            data = [[] for x in xrange(len(names))]
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

        self._signals = dict(zip(names[1:], signals[1:]))
        return self._signals
        
