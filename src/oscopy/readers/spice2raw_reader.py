

from oscopy import Signal
from .reader import Reader, ReadError
import struct
import io

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
            f = io.open(fn, 'r')
        except IOError as e:
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
        with io.open(self._fn, 'rb') as f:
            # Header
            signature = f.read(8).decode()
            title = f.read(80).strip(b'\x00').decode()
            res = f.read(22)
            (date, t, mode, nvars, const4) = struct.unpack('<2d3h' ,res)
            self._info.update(dict(list(zip(header_fields, (signature, title, date.decode(), t.decode(), mode.decode(), nvars.decode(), const4.decode())))))

            names = []
            for i in range(nvars):
                names.append(f.read(8).strip('#').strip(b'\x00').decode())
            types = struct.unpack('<%dh' % nvars, f.read(2 * nvars).decode())
            locs = struct.unpack('<%dh' % nvars, f.read(2 * nvars).decode())
            self._info['plottitle'] = f.read(24).strip(b'\x00')

            # Now we can create the signals
            signals = []
            for i in range(nvars):
                signals.append(Signal(names[i],
                                      self._types_to_unit.get(types[i], 'a.u.')))          
            # Data
            data = [[] for x in range(len(names))]
            # optimization: cache the append methods,
            # avoiding one dictionary lookup per line
            append = [x.append for x in data]
            while f:
                tmp = f.read(8 * nvars).decode()
                if len(tmp) < 8 * nvars: break
                values = struct.unpack('<%dd' % nvars, tmp)
                for i, v in enumerate(values):
                    append[i](v.decode())
            
        ref = signals[0]
        ref.data = data[0]
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]

        self._signals = dict(list(zip(names[1:], signals[1:])))
        print(self._signals)
        return self._signals

            
    
