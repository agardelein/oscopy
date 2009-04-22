""" Handle mathematical expressions for signals

In parent class, read validate the path, here validate the expression.
read_sigs() load the signals from file(s) and compute the expression.

Mathematical function are supported through the pylab module. However 
this module contains a bunch of non-math function, so only the functions
defined in the math modules are supported.

class MathReader:
   __init__(inp, sigs)
   Create a signal from expression with signals

   read(f)
   Validate the expression, check if all signals are here.

   read_sigs()
   Load the signals from files, and compute the result

   missing()
   Return the unrecognized name in the expression

   set_origsigs()
   Store the signals name and their original file to be used in read_sigs()

   check()
   No check to do since no file are used

   detect()
   Return true if argument is an expression with a '='

   validate_expr()
   Return True if the expression is valid, i.e. all elements are identified
"""

import numpy
import re
import math
import sys
from Reader import Reader
from Oscopy.Signal import Signal

class MathReader(Reader, object):
    def __init__(self, sigs={}):
        """ Create the object
        """
        self.slist = []
        self.origsigs = {}   # Dict of list of signames, key is filename
        self.set_origsigs(sigs)
        self.unkwn = []
        Reader.__init__(self)

    def read(self, inp=""):
        """ Validate the expression : each word should be in self.sigs
        or math module
        If read failed, return {} and unknown word can be retrieved by
        calling missing()
        """
        if not inp:
            return {}
        if self.validate_expr(inp):
            self.fn = inp
            return self.read_sigs()
        else:
            return {}

    def read_sigs(self):
        """ Return a dict with only the signal computed
        The signal is computed here since it can change between two updates
        """
        if not self.origsigs or not self.validate_origsigs():
            return {}

        _sigs = self.origsigs
        self.sigs = {}

        # Check homogeneity of X: signals should have the same abscisse
        first = 1
        inval = []
        for k, s in _sigs.iteritems():
            if first:
                _refname = s.ref.name
                _refdata = s.ref.data
                _refsig = s.ref
                first = 0
            else:
                # Check name
                if s.ref.name != _refname:
                    inval.append(k)
                    continue
                # Check values
                if len(_refdata) != len(s.ref.data):
                    inval.append(k)
                    continue
                for vref, v in zip(_refdata, s.ref.data):
                    if vref != v:
                        inval.append(k)
                        break
        if inval:
            print "Abscisse is different:",
            for s in inval:
                print s
            return {}
        del first, inval

        # Prepare the expression to be executed
        fn = self.fn
        # Replace sin with numpy.sin but only for supported math functions
        # an also fft with numpy.fft.fft
        # on: operand name
        for on in dir(math):
            fn = re.sub('\\b'+on+'\\b', 'numpy.'+on, fn)
        for on in ["fft", "ifft"]:
            fn = re.sub('\\b'+on+'\\b', 'numpy.fft.'+on, fn)
        for on in ["diff"]:
            fn = re.sub('\\b'+on+'\\b', 'numpy.'+on, fn)
        # Support for Time and Freq
        if fn.find("Time") > 0:
            Time = _refdata
            fn = re.sub('Time\(\w+\)', 'Time', fn)
        if fn.find("Freq") > 0:
            Freq = _refdata
            fn = re.sub('Freq\(\w+\)', 'Freq', fn)

        _expr = ""          # String for snippet code
        _endl = "\n"        # Newline code
        _ret = {}           # Value to be returned
        _sn = fn.split("=", 1)[0].strip()  # Result signal name
        _expr += "_tmp = Signal(\"" + _sn + "\")" + _endl
        for k, s in _sigs.iteritems():
            _expr += s.name + "=" + \
                "_sigs[\"" + s.name + "\"].data" + _endl
        _expr += fn + _endl
        _expr += "_tmp.data = " + _sn + _endl
        # If there is an fft or ifft, compute new axis
        if re.search("\\bfft\\b", fn) is not None\
                or re.search("\\bifft\\b", fn) is not None:
            if re.search("\\bifft\\b", fn) is None:
                # FFT
                _u = "Hz"
                _n = "Freq"
            else:
                # IFFT
                _u = "s"
                _n = "Time"
            # Result is symetric, only take one half
            _expr += "_len = int(len(_tmp.data) / 2 - 1)\n\
_tmp.data = _tmp.data[0:_len]\n\
# Compute reference signal\n\
_delta = abs(_refsig.data[1] \
- _refsig.data[0]) * len(_refsig.data)\n\
_x = numpy.linspace(0, _len, _len) / _delta\n"
            _expr += "_refsig = Signal(\"%s\", \"%s\")\n" % (_n, _u)
            _expr += "_refsig.data = _x\n"
        # If there is a diff, compute also new axis
        if re.search("\\bdiff\\b", fn) is not None:
            _expr += "_x = numpy.resize(_refsig.data, len(_refsig.data) - 1)\n\
_refsig = Signal(_refsig.name, _refsig.unit)\n\
_refsig.data = _x\n\
#print len(_refsig.data)\n\
#print len(_tmp.data)"
        _expr += "_tmp.ref = _refsig\n\
_ret[\"%s\"] = _tmp\n\
self.sigs[\"%s\"] = _tmp\n" % (_sn, _sn)

        # Execute the expression
#        print "Executing:\n---"
#        print _expr
#        print "---"
        try:
            exec(_expr)
        except NameError, e:
            print "NameError:", e.message
            return {}
        except TypeError, e:
            print "TypeError:", e.message
            return {}
        return _ret

    def missing(self):
        """ Return the unknown names found when read() was last called
        """
        return self.unkwn

    def set_origsigs(self, sigs={}):
        """ Update dependency signal dict only if there are missing
        """
        for sn, s in sigs.iteritems():
            if sn in self.unkwn:
                self.origsigs.update({sn:s})

    def get_depends(self):
        """ Return the list of signal names dependencies """
        return self.origsigs.keys()

    def check(self, fn):
        """ No file are needed, so no access problems !
        """
        return

    def detect(self, fn):
        """ If the filename contains "=", then this is managed
        """
        if fn.find("=") >= 0:
            return True
        else:
            return False

    def validate_expr(self, inp=""):
        """ Validate the expression
        Parse the expression if a word is not rocognized,
        add it to self.unkwn
        """
        # Allow Time and Freq keywords
        tf = ["Time", "Freq"]

        self.unkwn = []
        words = re.findall(r"(?i)\b[a-z0-9]*", inp.split("=")[1])
        for e in words:
            if e == "":
                # Nothing to evaluate
                continue
            if e in self.origsigs.keys():
                # Into the signal list
                continue
            elif e in dir(math):
                # Math function
                continue
            elif e.isdigit():
                # Number
                continue
            elif e in tf:
                # Other allowed names
                continue
            elif e in ["fft", "ifft"]:
                # FFT and inverse FFT
                continue
            elif e in ["diff"]:
                # diff
                continue
            else:
                # Unknown
                if re.match('[-+]?\d*\.?\d+([eE][-+]?\d+)?', e) is None:
                    self.unkwn.append(e)
                continue

        return len(self.unkwn) < 1

    def validate_origsigs(self):
        """ Return True if all the signals are valid, i.e. data is not None
        """
        for sn, s in self.origsigs.iteritems():
            if s.data is None or s.ref.data is None:
                return False
        return True
