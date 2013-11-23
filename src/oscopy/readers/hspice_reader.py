

import re
from oscopy import Signal
from .reader import Reader, ReadError
import struct, os

# ivar: independent variable (Time, Frequency)
# dvar: dependent variables (Signals)

class HspiceReader(Reader):
    """ Read Hspice binary and ascii format

Hspice can be either binary or ascii. Both types have a plain text header
containing various informations.

Note 1: Support only one sweep
Note 2: Auto signals are note returned, only probe signals are
Note 3: Endianness is not managed in binary mode

For more details see http://www.rvq.fr/linux/gawfmt.php    
    """
    _IVTYPE_UNIT = {'1': 's', '2': 'Hz', '3': 'V'}
    _DVTYPE_UNIT = {'1': 'V', '2': 'V', '8': 'A', '15': 'A', '22': 'A'}
    def detect(self, fn):
        """ Look at the header if it contains the five digits identificators

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
        with open(fn, 'rb') as f:
            nauto = f.read(4)
            if not nauto.isdigit():
                # Maybe a binary hpsice file ?
                f.seek(0, os.SEEK_SET)
                x = f.read(16)
                (h1, h2, h3, nbs) = struct.unpack('>4i', x) if len(x) == 16 else (0, 0, 0, 0)
                nauto = f.read(4)
            nprobe = f.read(4)
            nsweepparam = f.read(4)
            useless = f.read(4)
            version = f.read(4)
        return nauto.isdigit() and nprobe.isdigit()\
               and nsweepparam.isdigit()\
           and useless.isdigit() and useless == '0000'\
           and version.isdigit() and (version == '9007' or version == '9601')

    def _read_signals(self):
        """ Read the signals from the file

        Check whethers to read in binary of ascii mode and then call the
        relevant function
        
        Parameter
        ---------
        fn: string
        The filename

        Returns
        -------
        Dict of Signals
        The list of Signals read from the file
        """
        is_binary = False
        with open(self._fn, 'rb') as f:
            c = f.read(1)
            f.seek(0)
            if c < ' ':
                return self._read_binary(f)
            else:
                return self._read_ascii(f)

    def _read_binary(self, f):
        """ Read hspice file in binary format

        Note 1: Support only one sweep
        Note 2: Auto signals are note returned, only probe signals are
        Note 3: Endianness is not managed

        Parameter
        ---------
        f: file object
        The file to read from

        Returns
        -------
        self._signals: dict of Signals
        The Signals read from the file
        """
        (h, values) = self._read_block(f)
        (names, signals) = self._process_header(values)
        (h, values) = self._read_block(f)

        data = [[] for x in range(len(signals))]
        numsigs = self._nauto + self._nprobe
        datasize = h[3]
        nvals = datasize / 4 # sizeof(float)
        vals = struct.unpack('>%df' % nvals, values)

        for i in range(numsigs):
            start = i
            stop = nvals - numsigs + i
            step = numsigs
            data[i] = list(vals[start:stop:step])

        ref = signals[0]
        ref.data = data[0]
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]

        self._signals = dict(list(zip(names[self._nauto - 1:],\
                                 signals[self._nauto - 1:])))
        return self._signals

    def _read_ascii(self, f):
        """ Read hspice file in ascii format

        Note 1: Support only one sweep
        Note 2: Auto signals are note returned, only probe signals are

        Parameter
        ---------
        f: file object
        The file to read from

        Returns
        -------
        self._signals: dict of Signals
        The Signals read from the file
        """
        header = ''
        lines = iter(f)
        while header.find('$&%#') < 0:
            header = header + next(lines)
        (names, signals) = self._process_header(header)

        data = [[] for x in range(len(names))]
        # optimization: cache the append methods,
        # avoiding one dictionary lookup per line
        append = [x.append for x in data]
        count = 0
        n = self._nauto + self._nprobe
        for values in lines:
            for i, val in enumerate(values.split()):
                if val == '.10000E+31': break
                append[count % n](float(val))
                count = count + 1
            if val == '.10000E+31': break

        ref = signals[0]
        ref.data = data[0]
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]

        self._signals = dict(list(zip(names[self._nauto:],\
                                 signals[self._nauto:])))
        return self._signals

    def _read_block(self, f):
        """ Read one block of hspice binary file

        Note: endianness is not managed

        Parameter
        ---------
        f: file object
        The file to read from

        Returns
        -------
        tuple:
           h: tuple containing the first four integer of the block
              h1: int, endian indicator
              h2:
              h3: int, endian indicator
              nbs: next block size
           values: string
              block data as returned by file.read()
        """
        h = struct.unpack('>4i', f.read(16))
        (h1, h2, h3, nbs) = h
        values = f.read(nbs)
        pbs = struct.unpack('>i', f.read(4))
        return (h, values)

    def _process_header(self, header):
        """ Extract informations: signal names, number of variables...

        Parameter
        ---------
        header: string
        The string to parse containing the header of hspice file

        Returns
        -------
        tuple:
           dvnames: names of the signals
           signals: Signals instanciated while parsing the header
        This function set also:
           self._nauto: int, number of autovariables
           self._nprobe: int, number of user probes
           self._nsweepparam: int, number of sweep parameters
        """
        nauto = header[0:4]
        nprobe = header[4:8]
        nsweepparam = header[8:12]
        version = header[16:20]
        if version != '9007' and version != '9601' and \
                header[20:24] != '2001':
            raise NotImplementedError(_('hspice_reader: version \'%s\' not supported') % version)

        if header[20:24] == '2001':
            ntable_offset = 187
        else:
            ntable_offset = 176
        tmp = header[ntable_offset:].split()
        ntables = int(tmp[0])

        # Units
        ivunit = self._IVTYPE_UNIT.get(tmp[1], 'a.u')
        dvunits = [ivunit]
        for i in range(int(nauto) + int(nprobe) - 1):
            dvunits.append(self._DVTYPE_UNIT.get(tmp[i + 2], 'a.u.'))

        # Names
        offset = int(nauto) + int(nprobe) + 1
        ivname = tmp[offset]
        dvnames = [ivname]
        for i in range(int(nauto) + int(nprobe) - 1):
            dvnames.append(self._sanitize_name(tmp[i + offset + 1]))

        # Create Signals
        signals = []
        for i in range(len(dvunits)):
            signals.append(Signal(dvnames[i], dvunits[i]))

        # Return values
        (self._nauto, self._nprobe, self._nsweepparam) = (int(nauto),\
                                                          int(nprobe),\
                                                          int(nsweepparam))
        return (dvnames, signals)

    def _sanitize_name(self, name):
        """ Cleanup non-alphanumeric characters from string

        Parameter
        ---------
        name: string
        The name to sanitize

        Returns
        -------
        string
        The sanitized name
        """
        return name.replace('(', '').replace(')', '')\
                                   .replace('#', '').replace('+', '')\
                                   .replace('-', '')
