""" BaseGraph Handler

A graph consist of several signals that share the same abscisse,
and plotted according a to mode, which is currently scalar.

Signals are managed as a dict, where the key is the signal name.

In a graph, signals with a different sampling, but with the same abscisse
can be plotted together.

sn: signal name
s : signal

Class BaseGraph -- Handle the representation of a list of signals

   methods:
   __init__(sigs)
      Create a graph and fill it with the sigs

   __str__()
      Return a string with the list of signals, and abscisse name

   insert(sigs)
      Add signal list to the graph, set the abscisse name

   remove(sigs)
      Delete signals from the graph

   plot()
      Plot the graph

   getsigs()
      Return a list of the signal names

   setaxes()
      Define the type of the axes. To be overloaded by deriving classes.

   gettype()
      Return a string with the type of graph, to be overloaded.

"""

import matplotlib.pyplot as plt
from pylab import *

class BaseGraph:
    def __init__(self, sigs = None):
        """ Create a graph
        If signals are provided, fill in the graph otherwise the graph is empty
        Signals are assumed to exist and to be valid
        If first argument is a BaseGraph, then copy things
        """
        self.sigs = {}
        if isinstance(sigs, BaseGraph):
            mysigs = {}
            mysigs = sigs.sigs.copy()
            self.insert(mysigs)
            return
        else:
            self.xaxis = ""
            self.yaxis = ""
            if sigs == None:
                return
            else:
                self.insert(sigs)
                return

    def __str__(self):
        """ Return a string with the type and the signal list of the graph
        """
        a = "(" + self.gettype() + ") "
        for sn in self.sigs.keys():
            a = a + sn + " "
        return a

    def insert(self, sigs = None):
        """ Add a list of signals into the graph
        The first signal to be added defines the abscisse.
        The remaining signals to be added must have the same abscisse name,
        otherwise they are ignored
        """
        if sigs == None:
            return len(self.sigs)
        for sn, s in sigs.iteritems():
            if len(self.sigs) == 0:
                # First signal, set the abscisse name and add signal
                self.xaxis = s.ref.name
                self.xunit = s.ref.unit
                self.yaxis = "Signals"  # To change
                self.yunit = s.unit
                self.sigs[sn] = s
            else:
                if s.ref.name == self.xaxis:
                    # Add signal
                    self.sigs[sn] = s
                else:
                    # Ignore signal
                    print "Not the same ref:", sn, "-", self.xaxis,"-"
        return len(self.sigs)

    def remove(self, sigs = None):
        """ Delete signals from the graph
        """
        for sn in sigs.iterkeys():
            if sn in self.sigs.keys():
                del self.sigs[sn]
        return len(self.sigs)

    def plot(self):
        """ Plot the graph
        Each signal is plotted regarding to its proper abscisse.
        In this way, signals with a different sampling can be plotted together.
        The x axis is labelled with the abscisse name of the graph.
        """
        # Prepare the axis labels
        xl = self.xaxis
        xu = self.xunit
        fx, l = self.findscalefact("X")
        xl = xl + " (" + l + xu + ")"
        yl = self.yaxis
        yu = self.yunit
        fy, l = self.findscalefact("Y")
        yl = yl + " (" + l + yu + ")"
        
        self.setaxes()
        # Plot the signals
        hold(True)
#        mx = 0
#        my = 0
#        for s in self.itersigs():
#            try:
#                plot(s.ref.pts, s.pts, label=s.name)
#            except OverflowError, e:
#                print "OverflowError in plot:", e.message, ", log(0) somewhere ?"
#                break

        for sn, s in self.sigs.iteritems():
            # Scaling factor
            # The hard way...
            x = []
            for i in s.ref.pts:
                x.append(i * pow(10, fx))
            # The hard way, once again
            y = []
            for i in s.pts:
                y.append(i * pow(10, fy))
            try:
                plot(x, y, label=sn)
            except OverflowError, e:
                print "OverflowError in plot:", e.message, ", log(0) somewhere ?"
                hold(False)
                xlabel(xl)
                ylabel(yl)
                return
        hold(False)
        xlabel(xl)
        ylabel(yl)
        legend()

    def getsigs(self):
        """ Return a list of the signal names
        """
        for sn in self.sigs:
            yield sn

    def setaxes(self):
        """ Define the axes type, called by plot()
        To be overloaded by derived classes.
        """
        return

    def gettype(self):
        """ Return a string with the type of the graph
        To be overloaded by derived classes.
        """
        return
    
    def findscalefact(self, a):
        """ Choose the right scale for data on axis a
        Return the scale factor an a string with the abbrev.
        """
        scnames = {-18: "a", -15:"f", -12:"p", -9:"n", -6:"u", -3:"m", \
            0:"", 3:"k", 6:"M", 9:"G", 12:"T", 15:"P", 18:"E"}

        # Find the absolute maximum of the data
        mxs = []
        mns = []
        for s in self.sigs.itervalues():
            if a == "X":
                mxs.append(max(s.ref.pts))
                mns.append(min(s.ref.pts))
            else:
                mxs.append(max(s.pts))
                mns.append(min(s.pts))
        mx = abs(max(mxs))
        mn = abs(min(mns))
        mx = max(mx, mn)

        # Find the scaling factor using the absolute maximum
        if abs(mx) > 1:
            fct = -3
        else:
            fct = 3
        f = 0
        while not (abs(mx * pow(10, f)) < 1000 \
                       and abs(mx * pow(10, f)) > 1):
            f = f + fct
        if scnames.has_key(-f):
            l = scnames[-f]
        else:
            l = "10e" + str(-f)
        return f, l
