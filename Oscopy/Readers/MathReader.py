""" Handle mathematical expressions for signals

In parent class, read validate the path, here validate the expression.
readsigs() load the signals from file(s) and compute the expression.

Mathematical function are supported through the pylab module. However 
this module contains a bunch of non-math function, so only the functions
defined in the math modules are supported.

class MathReader:
   __init__(inp, sigs)
   Create a signal from expression with signals

   read(f)
   Validate the expression, check if all signals are here.

   readsigs()
   Load the signals from files, and compute the result

   missing()
   Return the unrecognized name in the expression

   set_origsigs()
   Store the signals name and their original file to be used in readsigs()

   check()
   No check to do since no file are used

   detect()
   Return true if argument is an expression with a '='
"""

import numpy
import re
import math
import sys
from Reader import Reader
from Oscopy.Signal import Signal

class MathReader(Reader):
    def __init__(self, sigs = {}):
        """ Create the object
        """
        self.slist = []
        self.origsigs = {}   # Dict of list of signames, key is filename
        self.set_origsigs(sigs)
        self.unkwn = []
        Reader.__init__(self)

    def read(self, inp = ""):
        """ Validate the expression : each word should be in self.sigs
        or math module
        If read failed, return {} and unknown word can be retrieved by
        calling missing()
        """
        if inp == "":
            return {}

        l=re.findall(r"(?i)\b[a-z0-9]*", inp.split("=")[1])
        vs = self.origsigs.keys()
        # Allow Time and Freq keywords
        tf = ["Time", "Freq"]
        self.unkwn = []
        for e in l:
            if e == "":
                # Nothing to evaluate
                continue
            if e in vs:
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
            else:
                # Unknown
                if re.match('[-+]?\d*\.?\d+([eE][-+]?\d+)?', e) == None:
                    self.unkwn.append(e)
                continue
        if len(self.unkwn) > 0:
            return {}
        self.fn = inp
        return self.readsigs()

    def readsigs(self):
        """ Return a dict with only the signal computed
        The signal is computed here since it can change between two updates
        """
        if self.origsigs == {}:
            return {}

        _sigs = self.origsigs

        # Check homogeneity of X: signals should have the same abscisse
        first = 1
        inval = []
        for k, s in _sigs.iteritems():
            if first:
                _refname = s.get_ref().get_name()
                _refdata = s.get_ref().get_data()
                _refsig = s.get_ref()
                first = 0
            else:
                # Check name
                if s.ref.name != _refname:
                    inval.append(k)
                    continue
                # Check values
                if len(_refdata) != len(s.get_ref().get_data()):
                    inval.append(k)
                    continue
                for vref, v in zip(_refdata, s.get_ref().get_data()):
                    if vref != v:
                        inval.append(k)
                        break
        if len(inval) > 0:
            print "Abscisse is different:",
            for s in inval:
                print s
            return {}
        del first, inval

        # Prepare the expression to be executed
        fn = self.fn
        # Replace sin with numpy.sin but only for supported math functions
        for on in dir(math):
             fn = re.sub('\\b'+on+'\\b', 'numpy.'+on, fn)
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
        _expr = _expr + "_tmp = Signal(\"" + _sn + "\", self)" + _endl
        _expr = _expr + "_data = []" + _endl
        for k, s in _sigs.iteritems():
            _expr = _expr + s.name + "=" + \
                "_sigs[\"" + s.name + "\"].get_data()" + _endl
        _expr = _expr + fn + _endl
        _expr = _expr + "_tmp.set_data("+ _sn +")" + _endl
        _expr = _expr + "_tmp.set_ref(_refsig)" + _endl
        _expr = _expr + "_ret[\"" + _sn + "\"] = _tmp" + _endl
        _expr = _expr + "self.slist.append(_tmp)" + _endl

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

    def set_origsigs(self, sigs = {}):
        """ Update dependency signal dict only if there are missing
        """
        for sn, s in sigs.iteritems():
            if sn in self.unkwn:
                self.origsigs.update({sn:s})

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
