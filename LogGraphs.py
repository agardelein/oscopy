""" LogGraphs -- A graph with logscale for X, Y or both

Class LogxGraph -- Draw graph with logscale for X axis only

   methods:
   setaxes()
      Set the X scale in log mode, and Y scale in lin mode

   gettype()
      Return the graph type, "logx"

   findscalefact(a)
      Return a scale factor for Y axis only

Class LogyGraph -- Draw graph with logscale for Y axis only

   methods:
   setaxes()
      Set the Y scale in log mode, and X scale in lin mode

   gettype()
      Return the graph type, "logy"

   findscalefact(a)
      Return a scale factor for X only

Class LoglogGraph -- Draw graph with logscale for X and y axis

   methods:
   setaxes()
      Set the X and Y scales in log mode

   gettype()
      Return the graph type, "loglog"

   findscalefact(a)
      Return no scale factor for both axes

Class FFTLogxGraph -- Draw graph with log scale on X and linear Y axis and FFT
   methods:
   setaxes()
      Set the X in log and Y scale in linear mode

   insert()
      Add signals to the graph after doing fft

   gettype()
      Return the mode of the graph, "fftlogx"

Class IFFTLogxGraph -- Draw graph with log scale on X and linear Y axis and IFFT
   methods:
   setaxes()
      Set the X in log and Y scale in linear mode

   insert()
      Add signals to the graph after doing inverse fft

   gettype()
      Return the mode of the graph, "ifftlogx"

Class FFTLogyGraph -- Draw graph with linear scale on X and log Y axis and FFT
   methods:
   setaxes()
      Set the X in linear and Y scale in log mode

   insert()
      Add signals to the graph after doing fft

   gettype()
      Return the mode of the graph, "fftlogy"

Class IFFTLogyGraph -- Draw graph with linear scale on X and log Y axis and IFFT
   methods:
   setaxes()
      Set the X in linear and Y scale in log mode

   insert()
      Add signals to the graph after doing inverse fft

   gettype()
      Return the mode of the graph, "ifftlogy"

Class FFTLoglogGraph -- Draw graph with log scale on X and Y axis and FFT
   methods:
   setaxes()
      Set the X and Y scale in log mode

   insert()
      Add signals to the graph after doing fft

   gettype()
      Return the mode of the graph, "fftloglog"

Class IFFTLinGraph -- Draw graph with log scale on X and Y axis and IFFT
   methods:
   setaxes()
      Set the X and Y scale in log mode

   insert()
      Add signals to the graph after doing inverse fft

   gettype()
      Return the mode of the graph, "ifftloglog"

"""

from Graph import *
from FFTGraph import *

class LogxGraph(Graph):
    def setaxes(self):
        """ The x axis is log, the y axis is linear
        """
        xscale("log")
        yscale("linear")

    def gettype(self):
        """ Return 'linear', the type of the graph
        """
        return "logx"

    def findscalefact(self, a):
        """ No scale factor for X axis
        """
        if a == "X":
            return 0, ""
        else:
            return Graph.findscalefact(self, a)

class LogyGraph(Graph):
    def setaxes(self):
        """ The y axis is log, the x axis is linear
        """
        xscale("linear")
        yscale("log")

    def gettype(self):
        """ Return 'logy', the type of the graph
        """
        return "logy"

    def findscalefact(self, a):
        """ No scale factor for Y axis
        """
        if a == "X":
            return Graph.findscalefact(self, a)
        else:
            return 0, ""

class LoglogGraph(Graph):
    def setaxes(self):
        """ The x and y axis are both log
        """
        xscale("log")
        yscale("log")

    def gettype(self):
        """ Return 'loglog', the type of the graph
        """
        return "loglog"

    def findscalefact(self, a):
        """ No scale factor for both axes
        """
        return 0, ""

class FFTLogxGraph(LogxGraph, FFTGraph):
    def setaxes(self):
        """ Logxear mode from LogxGraph
        """
        return LogxGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert FFT Signals from FFTGraph
        """
        return FFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "fftlogx"

class IFFTLogxGraph(LogxGraph, IFFTGraph):
    def setaxes(self):
        """ Semilogx mode from LogxGraph
        """
        return LogxGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert inverse FFT Signals from IFFTGraph
        """
        return IFFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "ifftlogx"

class FFTLogyGraph(LogyGraph, FFTGraph):
    def setaxes(self):
        """ Logxear mode from LogyGraph
        """
        return LogyGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert FFT Signals from FFTGraph
        """
        return FFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "fftlogy"

class IFFTLogyGraph(LogyGraph, IFFTGraph):
    def setaxes(self):
        """ Semilogy mode from LogyGraph
        """
        return LogyGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert inverse FFT Signals from IFFTGraph
        """
        return IFFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "ifftlogy"

class FFTLoglogGraph(LoglogGraph, FFTGraph):
    def setaxes(self):
        """ Logx mode from LoglogGraph
        """
        return LoglogGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert FFT Signals from FFTGraph
        """
        return FFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "fftloglog"

class IFFTLoglogGraph(LoglogGraph, IFFTGraph):
    def setaxes(self):
        """ Loglog mode from LoglogGraph
        """
        return LoglogGraph.setaxes(self)

    def insert(self, sigs):
        """ Insert inverse FFT Signals from IFFTGraph
        """
        return IFFTGraph.insert(self, sigs)

    def gettype(self):
        """ Return the type of the graph
        """
        return "ifftloglog"

