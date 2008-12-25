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

   setg(sigs)
      Set the signal list of the graphs

   fft()
      Do fft of signals before plotting

   iff()
      Do ifft of signal before plotting

   nofft()
      Do neither fft nor ifft
"""

from Axe import Axe
import matplotlib.pyplot as plt
from pylab import *
from scipy.fftpack import fft,ifft

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
            self.dofft = sigs.dofft
            return
        else:
            self.sigs = {}
            self.xaxis = ""
            self.dofft = 0
            if sigs == None:
                return
            else:
                self.insert(sigs)
                return

    def __str__(self):
        """ Return a string with the type and the signal list of the graph
        """
        a = self.gettype() + " "
        for n, s in self.sigs.iteritems():
            a = a + n
            a = a + " "
        return a

    def insert(self, sigs = None):
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

    def remove(self, sigs = None):
        """ Delete signals from the graph
        """
        for s in sigs:
            if s.name in self.sigs.keys():
                del self.sigs[s.name]
        return

    def update(self, u, d):
        """ Update the signals with reread values
        """
        for k, s in u.iteritems():
            self.sigs[k] = s
        for k in d:
            del self.sigs[k]
        return None

    def plot(self):
        """ Plot the graph
        Each signal is plotted regarding to its proper abscisse.
        In this way, signals with a different sampling can be plotted together.
        The x axis is labelled with the abscisse name of the graph.
        """
        self.setaxes()
        hold(True)
        for n, s in self.sigs.iteritems():
            if self.dofft == 0:
                x = s.ref.pts
                y = s.pts
            elif self.dofft > 0:
                y = fft(s.pts)
                y = y[0:int(len(y)/2)-1]
                x = []
                for i in range(0, len(y)):
                    x.append(i / (abs(s.ref.pts[1] - s.ref.pts[0]) \
                                      * len(s.ref.pts)))
                print "!!!!", len(x), len(y)
            else:
                y = ifft(s.pts)
                y = y[0:int(len(y)/2)-1]
                x = []
                for i in range(0, len(y)):
                    x.append(i / (abs(s.ref.pts[1] - s.ref.pts[0]) \
                                      * len(s.ref.pts)))
            plot(x, y)
        hold(False)
        xlabel(self.xaxis)

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
        return
    
    def setg(self, sigs = None):
        """ Set the signal dict
        The old signal list is deleted, as well as the abscisse name
        """
        self.sigs = {}
        self.xaxis = ""
        self.insert(sigs)

    def fft(self):
        """ Do a fft of signals before plotting
        """
        self.dofft = 1

    def ifft(self):
        """ Do a ifft of signals before plotting
        """
        self.dofft = -1

    def nofft(self):
        """ Do neither a fft or ifft before plotting
        """
        self.dofft = 0
