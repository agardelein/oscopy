from __future__ import with_statement

import re
from oscopy import Signal
from reader import Reader, ReadError
import struct

# ivar: independent variable (Time, Frequency)
# dvar: dependent variables (Signals)

class Spice3rawReader(Reader):
    """ Read Spice3 output files ascii and binary

Spice3 files can be binary or ascii. Both types have a plain text header
containing various informations. This Reader uses 'Flags', 'No. Variables',
'No. Points' and 'Variables'.

Supports real and complex numbers

Note: It supports only one simulation per file

For more details see http://www.rvq.fr/linux/gawfmt.php    
    """
    _types_to_unit = {'Time': 's', 'voltage': 'V', 'current': 'A', 'frequency': 'Hz'}
    _blocks = ['Plotname', 'Flags', 'No. Variables', 'No. Points', 'Command',
               'Variables', 'Title', 'Date']
    _flags = ['complex', 'real']
    
    def detect(self, fn):
        """ Look at the header if it contains the keyword 'Title:' at first line
        and 'Data:' at second line

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
        blocks = self._blocks
        nvar = 0
        with open(fn) as f:
            lines = iter(f)
            if lines.next().startswith('Title') and lines.next().startswith('Date'):
                return True
        return False

    def _read_signals(self):
        """ Read the signals from the file

        First get the reader and extract number, names and types of variables
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
        read_fun = None
        blocks = self._blocks
        data_read_fun = {'Binary': self._read_binary, 'Values': self._read_ascii}
        signals = []
        types = []
        names = []
        pos = 0 # Position of the data start
        with open(self._fn) as f:
            for line in f:
                pos = pos + len(line)
                # Parse the file
                words = line.split()
                word = words[0].rstrip(':')
                value = words[1] if len(words) > 1 else None
                if word.startswith('No.'):
                    # Lines starting with 'No. '
                    word = ' '.join((word, words[1].rstrip(':')))
                    value = words[2]
                if word in blocks:
                    # Header word
                    if word == 'No. Variables':
                        nvar = int(words[2])
                    elif word == 'Variables':
                        # Initialize Signals
                        for i in xrange(nvar):
                            x = f.next()
                            pos = pos + len(x)
                            x = x.split()
                            name = x[1].replace('(', '').replace(')', '')\
                                   .replace('#', '').replace('+', '')\
                                   .replace('-', '')
                            
                            signals.append(Signal(name, self._types_to_unit.get(x[2], 'a.u')))

                            names.append(name)
                    n = blocks.index(word)
                    self.info[word] = value
                elif word in data_read_fun.keys():
                    # Header processing finished
                    break
                else:
                    raise ReadError(_('Spice3raw_reader: unexpected keyword in header: \'%s\'') % word)

        # Can now read the data
        data = [[] for x in xrange(len(signals))]
        append = [x.append for x in data]

        data_read_fun[word](pos, append)

        ref = signals[0]
        ref.data = data[0]
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]

        self._signals = dict(zip(names[1:], signals[1:]))
        return self._signals
    
    def _read_binary(self, pos, append):
        """ Read the data from the file in binary mode.

        Data is read for the number of points defined in 'No. Points'.
        Data type is assumed to be 'double' whatever the type is (complex or
        real). This is in disagreement with http://www.rvq.fr/linux/gawfmt.php.

        Parameter
        ---------
        pos: integer
        The offset where to start reading the data

        append: list of append() methods
        List to use to store the data

        Returns
        -------
        append: list of append() methods
        """
        if self._info['Flags'] not in self._flags:
                raise ReadError(_('Spice3raw_reader: unexpected value for keyword \'Flags\': %s')% (self._info['Flags']))

        is_complex = (self._info['Flags'] == 'complex')
        nvars = int(self._info['No. Variables']) * (2 if is_complex else 1)
        n = int(self._info['No. Points']) # Data counter

        with open(self._fn) as f:
            # print pos, '(0x%04x)'% pos
            f.seek(pos)
            while f and n:
                tmp = f.read(8 * nvars)
                if len(tmp) < 8 * nvars: break
                values = struct.unpack('<%dd' % nvars, tmp)
                n = n - 1
                if is_complex:
                    for i, v in enumerate(values[::2]):
                        append[i](complex(v, values[2*i+1]))
                else:
                    for i, v in enumerate(values):
                        append[i](v)
        return append

    def _read_ascii(self, pos, append):
        """ Read the data from the file in ascii mode.

        Data is read for the number of points defined in 'No. Points'.

        Parameter
        ---------
        pos: integer
        The offset where to start reading the data

        append: list of append() methods
        List to use to store the data

        Returns
        -------
        append: list of append() methods
        """
        is_complex = (self._info['Flags'] == 'complex')
        nvars = int(self._info['No. Variables']) * (2 if is_complex else 1)
        n = int(self._info['No. Points']) # Data counter

        with open(self._fn) as f:
            f.seek(pos)
            while f and n:
                values = f.next()
                x = values.split()
                if len(x) > 1:
                    # Get the ivar
                    append[0](float(x[1]))
                    n = n - 1
                    for i in xrange(1, nvars):
                        # And the dvars
                        values = f.next().split()
                        if is_complex:
                            append[i](complex(float(values[0]), float(values[1])))
                        else:
                            append[i](float(values[0]))
        return append
    
