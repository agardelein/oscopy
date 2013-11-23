from __future__ import with_statement

import re
import io
from oscopy import Signal
from reader import Reader, ReadError
import struct, os

class TouchstoneReader(Reader):
    """ Read Touchstone(r) or snp file format, version 1 and 2.0

Noise parameter data is read and stored in self.info['noise_param'].

Mixed mode parameters of version 2.0 not supported.

Note: this Reader uses the file extension to determine the number of ports
for version 1 of this format specification ('.snp' where n is 1-4)

For more details, see http://www.eda.org/ibis/touchstone_ver2.0/touchstone_ver2_0.pdf
    """

    FREQ_UNIT_VALUES = {'HZ': 1, 'KHZ': 1e3, 'MHZ': 1e6, 'GHZ': 1e9}
    PARAM_VALUES = ['S', 'Y', 'Z', 'H', 'G']
    FORMAT_VALUES = {'DB': ('dB', 'degrees'), 'MA': ('a.u.', 'degrees'),
                     'RI': ('a.u.', 'a.u')}
    KEYWORDS = ['version', 'number of ports', 'two-port data order',
                'number of frequencies', 'number of noise frequencies',
                'reference', 'matrix format', 'mixed-mode order',
                'begin information', 'end information',
                'network data', 'noise data', 'end']
    MATRIX_FORMAT = ['full', 'lower', 'upper']
    EXT_PORTS = {'s1p': 1, 's2p': 2, 's3p': 3, 's4p': 4}
    
    def detect(self, fn):
        """ Search for the option line (starting with '#') and returns result
        of processing this line.

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
        while f:
            line = f.readline().strip()
            if not line or line.startswith('!'):
                continue
            elif line.startswith('#'):
                return (self._process_option(line) is not None)
            elif line.startswith('['):
                continue
            else:
                f.close()
                return False
        f.close()
        return True
    
    def _read_signals(self):
        """ Read the signals from the file

        Check whether file format is version 1 or 2 (detection of '[')
        and parse the option line when met then call the relevant
        function to read the data.

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
        options = self._process_option('#')
        version = 1
        with io.open(self._fn, 'r') as f:
            data_start = False
            while not data_start:
                line = f.readline().strip()
                if not line:
                    continue
                if line.startswith('!'):
                    continue
                elif line.startswith('#'):
                    options = self._process_option(line)
                elif line.startswith('['):
                    if line.split()[0].lower() == '[' + self.KEYWORDS[0] + ']':
                        version = float(line.split()[1])
                elif line.split()[0][0].isdigit():
                    break
            f.seek(0)
            if version == 1:
                return self._read_signals_v1(f, options, len(line.split()))
            elif version == 2:
                return self._read_signals_v2(f, options)
            else:
                raise NotImplementedError(_('touchstone_reader: format version %s not supported' % version))

    def _process_option(self, line):
        """ Parse the option line

        Parameter
        ---------
        line: string
        the line containing the options

        Returns
        -------
        options: dict
        The list of parameters extracted from option line
           'freq_mult': float
              The frequency multiplier, e.g. 1e9 for GHz
           'param': string
              The parameter measured, e.g. 'S' for S-parameter
           'format': string
              The file format, e.g. 'MA' for Magnitude-Angle
           'ref': float
              The value of reference resistance
        """
        options = {'freq_mult': 1e9, 'param': 'S', 'format': 'MA', 'ref': 50}
        opts = line.lstrip('#').upper().split()
        r_found = False
        for opt in opts:
            if opt in self.FREQ_UNIT_VALUES.keys():
                options['freq_mult'] = self.FREQ_UNIT_VALUES[opt]
            elif opt in self.PARAM_VALUES:
                options['param'] = opt
            elif opt in self.FORMAT_VALUES.keys():
                options['format'] = opt
            elif opt == 'R':
                r_found = True
            elif r_found:
                options['ref'] = float(opt)
            else:
                return None #Keyword not recognized
        return options

    def _read_signals_v1(self, f, options, n = 3):
        """ Read file using Touchstone 1.0 format specification

        Noise parameters stored in self._info['noise_param']

        Parameters
        ----------
        f: file
        The file object (already opened) to read data from

        options: dict
        Parameters from option line. Used here: 'format', 'param', 'freq_mult'

        n: int
        Number of word on first line found with first character being a digit
        assumed to be the first data line

        Returns
        -------
        self._signals: dict of Signals

        Raises
        ------
        ReadError
        Unknown number of ports
        """
        # Guess number of ports, inspired from W. hoch's dataplot
        extension = self._fn.split('.')[-1].lower()
        nports = self.EXT_PORTS.get(extension, None)
        if nports is None:
            # Not found in extension, guess from number of data on first line,
            # but works only for 1-port and 2-port
            nports = {3: 1, 9: 2}.get(n, None)
            if nports is None:
                raise ReadError(_('touchstone_reader: unknown number of ports'))

        # Instanciate signals
        (ref, signals, names) = self._instanciate_signals(nports, options)

        # Read data
        nparams = len(signals)
        data = [[] for x in xrange(len(signals))]
        append = [x.append for x in data]
        cpt = 0
        offset = 0
        noise_param = []
        np_append = noise_param.append
        for line in f:
            if not len(line) or line.startswith('!') or line.startswith('#'):
                continue
            elif len(line.split()) == 5:
                # A line of noise parameter data
                np_append([float(x) for x in line.split()])
            else:
                # Network parameter data
                for i, val in enumerate(line.split()):
                    if val.startswith('!'):
                        # Comments at end of line so next line
                        break
                    append[offset + i](float(val))
                    cpt = cpt + 1
                if cpt < nparams:
                    # line is not finished, remaining parameters on next line
                    offset = cpt
                else:
                    cpt = offset = 0

        # Gather data
        ref.data = data[0]
        ref.data = ref.data * options['freq_mult']
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]
        self._signals = dict(zip(names[1:], signals[1:]))
        
        self._info['noise_param'] = self._process_noise_param(noise_param, 1)
        return self._signals

    def _read_signals_v2(self, f, options):
        """ Read file using Touchstone 2.0 format specification

        Noise parameters stored in self._info['noise_param'] unprocessed
        Keywords met stored in self._info

        Parse the file line by line, and when relevant keyowrds are met, store
        network data or noise parameter data.

        Parameters
        ----------
        f: file
        The file object (already opened) to read data from

        options: dict
        Parameters from option line. Used here: 'format', 'param', 'freq_mult'

        n: int
        Number of word on first line found with first character being a digit
        assumed to be the first data line

        Returns
        -------
        self._signals: dict of Signals

        Raises
        ------
        ReadError
        unkown string, unknown keyword or argument, excess of reference values
        """
        data_start = False
        noise_start = False
        end = False
        noise_param = []
        np_append = noise_param.append
        for line in f:
            if not len(line) or line.startswith('!') or line.startswith('#'):
                # Blank line or comment
                continue

            elif line.strip().startswith('['):
                # Keyword. Extract keyword and argument, check if kw is valid,
                # store it in self._info, then process the keyword if needed
                tmp = re.findall('\[([\w\s-]+)\]\s*(\S*)', line.strip())
                if not tmp:
                    raise ReadError(_('touchstone_reader: unrecognized \'%s\'') % line)
                kw = tmp[0][0]
                arg = tmp[0][1] if len(tmp[0]) > 1 else ''
                if kw.lower() not in self.KEYWORDS:
                    raise ReadError(_('touchstone_reader: unrecognized keyword \'%s\'') % kw)
                self._info[kw.lower()] = arg
                # Keyword neededs addtionnal process
                if kw.lower() == 'network data':
                    # Next line will be data, prepare the signals and variables
                    # used for reading
                    (ref, signals, names) = self._instanciate_signals(nports,
                                                                      options)
                    data = [[] for x in xrange(len(signals))]
                    append = [x.append for x in data]
                    mxfmt = self._info.get('matrix format', 'full').lower()
                    row = 0
                    data_start = True
                elif kw.lower() == 'noise data':
                    # Next line will be noise data
                    noise_start = True
                    data_start = False
                elif kw.lower() == 'end':
                    # No more data to read
                    break
                elif kw.lower() == 'reference':
                    # Assuming [Reference] keyword is without spaces
                    self._info['reference'] = [float(x.strip()) for x in line.split()[1:]]
                elif kw.lower() == 'number of ports':
                    nports = int(self._info['number of ports'])
                elif kw.lower() == 'number of frequencies':
                    nfreq = int(self._info['number of frequencies'])
                elif kw.lower() == ['matrix format']:
                    # Validate the argument
                    if arg.lowrer() not in self.MATRIX_FORMATS:
                        raise ReadError(_('touchstone_reader: unrecognized matrix format \'%s\'') % mxfmt)
                        
            elif data_start:
                # Data, assume on row per line for matrices
                tmp = line.partition('!')[0]  # Remove any comment
                if mxfmt in ['full', 'lower']:
                    offset = 0 if not row else nports * 2 * row + 1
                else: # mxfmt == 'upper'
                    # Not tested
                    offset = 0 if not row else nports * 2 * row + 1 + row * 2
                for i, val in enumerate(tmp.split()):
                    append[i + offset](float(val))
                row = (row + 1) if row < nports and nports > 2 else 0

            elif noise_start:
                # Noise
                np_append([float(x) for x in line.split()])

            elif len(self._info.get('reference', nports)) < nports:
                # Reference on more than a line
                tmp = line.split()
                if len(tmp) > len(self._info['reference']):
                    raise ReadError(_('touchstone_reader: excess references found \'%s\'') % line)
                for x in tmp:
                    self.info['reference'].append(float(x.strip()))
        if mxfmt in ['lower', 'upper']:
            # Expand matrices in case of 'upper' or 'lower'
            for i in xrange(nports):
                for j in xrange(nports):
                    if mxfmt == 'lower' and i < j:
                        data[i * nports * 2 + j * 2 + 1] = data[j * nports * 2 + i * 2 + 1]
                        data[i * nports * 2 + j * 2 + 2] = data[j * nports * 2 + i * 2 + 2]
                    if mxfmt == 'upper' and i > j:
                        data[i * nports * 2 + j * 2 + 1] = data[j * nports * 2 + i * 2 + 1]
                        data[i * nports * 2 + j * 2 + 2] = data[j * nports * 2 + i * 2 + 2]

        # Gather data
        ref.data = data[0]
        ref.data = ref.data * options['freq_mult']
        for i, s in enumerate(signals[1:]):
            s.ref = ref
            s.data = data[i + 1]
        self._signals = dict(zip(names[1:], signals[1:]))

        self._info['noise_param'] = self._process_noise_param(noise_param, 2)
        return self._signals
    
    def _instanciate_signals(self, nports, options):
        """ Instanciate the signals depending on number of port and type
        of measurement in the form of Xij_n where X is the parameter, i and
        j the indices and n is either 'a' or 'b'.

        Parameters
        ----------
        nports: int
        Number of ports

        options: dict
           'param': string
           The parameter stored in file (e.g. S, Z, H...)

        Returns
        -------
        tuple:
           ref: Signal
           The reference signal

           signals: list of Signals
           Signals instanciated

           names: list of strings
           Names of the Signals instanciated, same order as 'signals'
        """
        ref = Signal('Frequency', 'Hz')
        signals = [ref]
        names = [ref.name]
        for p1 in xrange(nports):
            for p2 in xrange(nports):
                name = options['param'] + '%1d' % (p1 + 1) + '%1d' % (p2 + 1)
                (unit_a, unit_b) = self.FORMAT_VALUES[options['format']]
                signal_a = Signal(name + '_a', unit_a)
                signal_b = Signal(name + '_b', unit_b)
                signals.append(signal_a)
                signals.append(signal_b)
                names.append(name + '_a')
                names.append(name + '_b')
        return (ref, signals, names)

    def _view_matrix(self, data, names, nports):
        """ View X parameter matrix, debug only

        Parameters
        ----------
        data: list of list of float
        The matrix to be viewed

        names: list of strings
        The names of the Signals that will be instanciated

        nports: int
        The number of ports, i.e. matrix rank

        Returns
        -------
        Nothing
        """
        for i in xrange(nports):
            for j in xrange(nports):
                print names[i * nports * 2 + j * 2 + 1], names[i * nports * 2 + j * 2 + 2], 
                print data[i * nports * 2 + j * 2 + 1], data[i * nports * 2 + j * 2 + 2],
            print
                

    def _process_noise_param(self, np, version):
        """ Process noise parameter data and returns a dict of Signals

        Version of format is requested as in version 1 the effective noise
        resistance is normalized while in version 2 it is not

        Parameters
        ----------
        np: list of list of float
        The noise parameter data as read

        version: int
        Format version of the file

        Returns
        -------
        ret: dict of Signals
           'minnf': Minimum noise figure
           'Refl_coef_a'
           'Refl_coef_b': Source reflection coefficient to realize minimum
                          noise figure
           'R_neff': Effective noise resistance
        """
        freq = Signal('Frequency', 'Hz')
        minnf = Signal('minnf', 'dB')
        reflcoefa = Signal('Refl_coef_a', 'a.u.')
        reflcoefb = Signal('Refl_coef_b', 'degrees')
        effnr = Signal('R_neff', 'a.u.' if version == 1 else 'Ohm')

        sigs = [freq, minnf, reflcoefa, reflcoefb, effnr]

        noise_param = [[] for x in xrange(5)]
        append = [x.append for x in noise_param]

        for p in xrange(len(np)):
            for i, a in enumerate(append):
                a(np[p][i])

        freq.data = noise_param[0]
        for i, s in enumerate(sigs[1:]):
            s.ref = freq
            s.data = noise_param[i + 1]

        ret = {'Frequency': freq, 'minnf': minnf,
                       'Refl_coef_a': reflcoefa, 'Refl_coef_b': reflcoefb,
                       'R_neff': effnr}
        return ret
