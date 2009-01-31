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

   setorigsigs()
   Store the signals name and their original file to be used in readsigs()

   detect()
   Return true if argument is an expression with a '='
"""

import Reader
import DetectReader
import Signal
import numpy
import re
import math
import sys
#sys.path.insert(0, '..')

class MathReader(Reader.Reader):
    def __init__(self, sigs = {}):
        """ Create the object
        """
        self.slist = []
        self.origsigs = {}   # Dict of list of signames, key is filename
        self.setorigsigs(sigs)
        self.unkwn = []
        Reader.Reader.__init__(self)

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
            else:
                # Unknown
                self.unkwn.append(e)
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
                _refname = s.getref().getname()
                _refpts = s.getref().getpts()
                _refsig = s.getref()
                first = 0
            else:
                # Check name
                if s.ref.name != _refname:
                    inval.append(k)
                    continue
                # Check values
                if len(_refpts) != len(s.getref().getpts()):
                    inval.append(k)
                    continue
                for vref, v in zip(_refpts, s.getref().getpts()):
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
        # Replace sin with pylab.sin but only for supported math functions
        for on in dir(math):
             fn = re.sub('\\b'+on+'\\b', 'numpy.'+on, fn)

        _expr = ""          # String for snippet code
        _endl = "\n"        # Newline code
        _ret = {}           # Value to be returned
        _sn = fn.split("=", 1)[0].strip()  # Result signal name
        _expr = _expr + "_tmp = Signal.Signal(\"" + _sn + "\", self)" + _endl
        _expr = _expr + "_pts = []" + _endl
        _expr = _expr + "# The slow way" + _endl
#        _expr = _expr + "for _i in range(0, len(_refpts)):" + _endl
        for k, s in _sigs.iteritems():
            _expr = _expr + s.name + "=" + \
                "_sigs[\"" + s.name + "\"].getpts()" + _endl
        _expr = _expr + fn + _endl
#        _expr = _expr + "\t_pts.append(" + _sn +")" + _endl
        _expr = _expr + "_tmp.setpts("+ _sn +")" + _endl
        _expr = _expr + "_tmp.setref(_refsig)" + _endl
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

    def setorigsigs(self, sigs = {}):
        """ Update dependency signal dict only if there are missing
        """
        for sn, s in sigs.iteritems():
            if sn in self.unkwn:
                self.origsigs.update({sn:s})

    def detect(self, fn):
        """ If the filename contains "=", then this is managed
        """
        if fn.find("=") >= 0:
            return True
        else:
            return False
