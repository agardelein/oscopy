""" Handle mathematical expressions for signals

The implementation is quite unoptimized to simplify the use of update()

In parent class, read validate the path, here validate the expression.
readsigs() load the signals from file(s) and compute the expression.

class MathReader:
   __init__(inp, sigs)
      Create a signal from expression with signals

   read(f)
      Validate the expression, check if all signals are here.

   readsigs()
      Load the signals from files, and compute the result

   setorigsigs()
      Store the signals name and their original file to be used in readsigs()
"""

import Reader
import DetectReader
import Signal
import pylab
import re
import math
import sys
#sys.path.insert(0, '..')

class MathReader(Reader.Reader):
    def __init__(self, sigs = {}):
        """ Create the object
        """
        self.fn = ""
        self.slist = []
        self.origsigs = {}   # Dict of list of signames, key is filename
        self.setorigsigs(sigs)

    def read(self, inp = ""):
        """ Validate the expression : each word should be in self.sigs
        or math module
        """
        if self.origsigs == {}:
            return {}

        if inp == "":
            return {}

        l=re.findall(r"(?i)\b[a-z0-9]*", inp.split("=")[1])
        vs = []
        for v in self.origsigs.values():
            # Create a single list of signals from self.origsigs.values()
            # which is a list of lists
            vs.extend(v)
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
                print "What's this", e, "?"
                return {}
        self.fn = inp
        return self.readsigs()

    def readsigs(self):
        """ Return a dict with only the signal computed
        The signal is done here since it can change between two updates
        """
        if self.origsigs == {}:
            return {}

        _sigs = {}
        # Read the signals from the files
        for f, snames in self.origsigs.iteritems():
            r = DetectReader.DetectReader(f)
            if hasattr(r, "setorigsigs"):
                if callable(r.setorigsigs):
                    r.setorigsigs(self.origsigs)
            sigsfile = r.read(f)
            for s in snames:
                if s in sigsfile.keys():
                    _sigs[s] = sigsfile[s]
                else:
                    print "Signal", s, "not found anymore in", f, "! "\
                        "Not updating", self.fn.split("=", 1)[0].strip()
                    return {}
        
        # Check homogeneity of X: signals should have the same abscisse
        first = 1
        inval = []
        for k, s in _sigs.iteritems():
            if first:
                _refname = s.ref.name
                _refpts = s.ref.pts
                _refsig = s.ref
                first = 0
            else:
                # Check name
                if s.ref.name != _refname:
                    inval.append(k)
                    continue
                # Check values
                if len(_refpts) != len(s.ref.pts):
                    inval.append(k)
                    continue
                for vref, v in zip(_refpts, s.ref.pts):
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
        _expr = ""          # String for snippet code
        _endl = "\n"        # Newline code
        _ret = {}           # Value to be returned
        _sn = self.fn.split("=", 1)[0].strip()  # Result signal name
        _expr = _expr + "_tmp = Signal.Signal(\"" + _sn + "\")" + _endl
        _expr = _expr + "_tmp.pts = []" + _endl
        _expr = _expr + "# The slow way" + _endl
        _expr = _expr + "for _i in range(0, len(_refpts)):" + _endl
        for k, s in _sigs.iteritems():
            _expr = _expr + "\t" + s.name + "=" + \
                "_sigs[\"" + s.name + "\"].pts[_i]" + _endl
        _expr = _expr + "\t" + self.fn + _endl
        _expr = _expr + "\t_tmp.pts.append(" + _sn +")" + _endl
        _expr = _expr + "_tmp.ref = _refsig" + _endl
        _expr = _expr + "_tmp.reader = self" + _endl
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

    def setorigsigs(self, sigs = {}):
        """ Get the filenames and the signal names from the list of signals
        Key is filename, values are signals.
        """

        for k, s in sigs.iteritems():
            f = s.reader.fn
            n = s.name
            if self.origsigs.has_key(f):
                self.origsigs[f].append(n)
            else:
                self.origsigs[f] = [n]

    def detect(self, fn):
        """ If the filename contains "=", then this is managed
        """
        if fn.find("=") >= 0:
            return True
        else:
            return False
