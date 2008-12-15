""" BaseGraph Handler

A graph consist of several signals that share the same abscisse,
and plotted according a to mode, which is currently scalar.

Signals are managed as a dict, where the key is the signal name.

In a graph, signals with a different sampling, but with the same abscisse
can be plotted together.

Class BaseGraph -- Handle the representation of a list of signals

   methods:
   __init__(sigs)
      Create a graph and fill it with the sigs

   add(sigs)
      Add signal list to the graph, set the abscisse name

   setg(sigs)
      Set the signal list of the graphs

   plot()
      Plot the graph

   __str__()
      Return a string with the list of signals, and abscisse name

   setaxes()
      Define the type of the axes. To be overloaded by deriving classes.
"""

from Axe import Axe
import matplotlib.pyplot as plt
from pylab import *

class BaseGraph:
    def __init__(self, sigs = None):
        """ Create a graph
        If signals are provided, fill in the graph otherwise the graph is empty
        Signals are assumed to exist and to be valid
        If first argument is a BaseGraph, then copy things
        """
        if isinstance(sigs, BaseGraph):
            self.sigs = sigs.sigs
            self.xaxis = sigs.xaxis
            return
        else:
            self.sigs = {}
            self.xaxis = ""
            if sigs == None:
                return
            else:
                self.add(sigs)
                return

    def add(self, sigs = None):
        """ Add a list of signals into the graph
        The first signal to be added defines the abscisse.
        The remaining signals to be added must have the same abscisse name,
        otherwise they are ignored
        """
        if sigs == None:
            return
        for s in sigs:
            if len(self.sigs) == 0:
                # First signal, set the abscisse name and add signal
                self.xaxis = s.ref.name
                self.sigs[s.name] = s
            else:
                if s.ref.name == self.xaxis:
                    # Add signal
                    self.sigs[s.name] = s
                else:
                    # Ignore signal
                    print "Not the same ref:", s.name, "-", self.xaxis,"-"

    def setg(self, sigs = None):
        """ Set the signal dict
        The old signal list is deleted, as well as the abscisse name
        """
        self.sigs = {}
        self.xaxis = ""
        self.add(sigs)

    def plot(self):
        """ Plot the graph
        Each signal is plotted regarding to its proper abscisse.
        In this way, signals with a different sampling can be plotted together.
        The x axis is labelled with the abscisse name of the graph.
        """
        self.setaxes()
        hold(True)
        for n, s in self.sigs.iteritems():
            x = s.ref.pts
            y = s.pts
            plot(x, y)
        hold(False)
        xlabel(self.xaxis)

    def __str__(self):
        """ Return a string with the type and the signal list of the graph
        """
        a = self.gettype() + " "
        for n, s in self.sigs.iteritems():
            a = a + n
            a = a + " "
        return a

    def update(self, u, d):
        """ Update the signals with reread values
        """
        for k, s in u.iteritems():
            self.sigs[k] = s
        for k in d:
            del self.sigs[k]
        return None

    def getsigs(self):
        """ Return a list of the signal names
        """
        return self.sigs.keys()

    def setaxes(self):
        """ Define the axes type, called by plot()
        To be overloaded by derived classes.
        """
        return
    def gettype(self):
        """ Return a string with the type of the graph
        To be overloaded by derived classes.
        """
