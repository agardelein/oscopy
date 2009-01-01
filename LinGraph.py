""" A graph with linear scale on X and Y axis

Class LinGraph -- Draw graph with linear scale on X and Y axis

   methods:
   setaxes()
      Set the X and Y scale in linear mode

   gettype()
      Return the mode of the graph "linear"

Class FFTLinGraph -- Draw graph with linear scale on X and Y axis and FFT
   methods:
   setaxes()
      Set the X and Y scale in linear mode

   insert()
      Add signals to the graph after doing fft

   gettype()
      Return the mode of the graph, "fftlin"

Class IFFTLinGraph -- Draw graph with linear scale on X and Y axis and IFFT
   methods:
   setaxes()
      Set the X and Y scale in linear mode

   insert()
      Add signals to the graph after doing inverse fft

   gettype()
      Return the mode of the graph, "ifftlin"
"""

from BaseGraph import *
from FFTGraph import *

class LinGraph(BaseGraph):
    def setaxes(self):
        """ Set the X and Y axis in linear mode
        """
        xscale('linear')
        yscale('linear')

    def gettype(self):
        """ Return 'linear', the type of the graph
        """
        return "linear"

class FFTLinGraph(LinGraph, FFTGraph):
    def setaxes(self):
        """ Linear mode from LinGraph
        """
        return LinGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert FFT Signals from FFTGraph
        """
        return FFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "fftlin"

class IFFTLinGraph(LinGraph, IFFTGraph):
    def setaxes(self):
        """ Linear mode from LinGraph
        """
        return LinGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert inverse FFT Signals from IFFTGraph
        """
        return IFFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "ifftlin"
