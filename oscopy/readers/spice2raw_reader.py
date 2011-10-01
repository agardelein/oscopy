from __future__ import with_statement

from oscopy import Signal
from reader import Reader, ReadError
import struct

class Spice2rawReader(Reader):
    """ Read Berkeley Spice2G6 'raw' output files

    Currently support only one dataset per file
    Date and Time fields are not processed

    see http://www.rvq.fr/linux/gawfmt.php for format description
    """
    _signature = 'rawfile1'
    _types_to_unit = {0: 'a.u.', 1: 's', 2: 'V', 3: 'A', 4: 'Hz', 5: 'a.u.'}
    def detect(self, fn):
        """ Look at the header if it contains the keyword self._signature

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
            f = open(fn)
        except IOError, e:
            return False
        s = f.read(8)
        f.close()
        return s == self._signature

    def _read_signals(self):
        """ Read the signals from the file

        Supports only one dataset per file

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
        header_fields = ['signature', 'title', 'date', 'time',
                         'mode', 'nvars', 'const4']
        with open(self._fn) as f:
            # Header
            signature = f.read(8)
            title = f.read(80).strip('\x00')
            res = f.read(22)
            (date, t, mode, nvars, const4) = struct.unpack('<2d3h' ,res)
            self._info.update(dict(zip(header_fields, (signature, title, date, t, mode, nvars, const4))))

            names = []
            for i in xrange(nvars):
                names.append(f.read(8).strip('#').strip('\x00'))
            types = struct.unpack('<%dh' % nvars, f.read(2 * nvars))
            locs = struct.unpack('<%dh' % nvars, f.read(2 * nvars))
            self._info['plottitle'] = f.read(24).strip('\x00')

            # Now we can create the signals
            signals = []
            for i in xrange(nvars):
                signals.append(Signal(names[i],
                                      self._types_to_unit.get(types[i], 'a.u.')))          
            # Data
            data = [[] for x in xrange(len(names))]
            # optimization: cache the append methods,
            # avoiding one dictionary lookup per line
            append = [x.append for x in data]
            while f:
                tmp = f.read(8 * nvars)
                if len(tmp) < 8 * nvars: break
                values = struct.unpack('<%dd' % nvars, tmp)
                for i, v in enumerate(values):
                    append[i](v)
            
        ref = signals[0]
        ref.data = data[0]
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]

        self._signals = dict(zip(names[1:], signals[1:]))
        print self._signals
        return self._signals

            
    
