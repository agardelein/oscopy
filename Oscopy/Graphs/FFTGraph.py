""" A graph with FFT or inverse FFT

Class FFTGraph -- Do an fft when plotting

   methods:
   plot()
   Plot the fft of the signals

   gettype()
   Return "fft", the type of the graph

Class IFFTGraph -- Do an inverse fft when plotting signals

   methods:
   plot()
   Plot the inverse fft of signals

   gettype()
   Return "ifft", the type of the graph
"""
from Graph import Graph
from Oscopy.Signal import Signal
import numpy.fft

class FFTGraph(Graph):

    def plot(self):
        """ Plot the fft of signals.
        First calculate the fft of each signal
        and then call the parent function
        """
        # Save signals
        origsigs = self.sigs
        self.sigs = {}
        # Compute FFT for all signals
        for sn, s in origsigs.iteritems():
            s2 = Signal(sn, None, s.getunit())
            # Check whether ref sig is Time
            if s.getref().getname() != "Time":
                print "Warning : ref sig of", s.getname() ,"is not 'Time'.\
 I hope you know what you do !"
            # Do a fft
            y = numpy.fft.fft(s.getpts())
            y = y[0:int(len(y)/2)-1]
            s2.setpts(y)
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.getref().getpts()[1]\
                                      - s.getref().getpts()[0])\
                                  * len(s.getref().getpts())))
            s2.setref(Signal("Freq", None, "Hz"))
            s2.getref().setpts(x)
            self.sigs[sn] = s2

        self.xunit = "Hz"
        self.xaxis = "Freq"
        Graph.plot(self)

        # Restore signals
        self.sigs = origsigs
        return

    def gettype(self):
        """ Return the type of graph, here fft
        """
        return "fft"

class IFFTGraph(Graph):
    def gettype(self):
        """ Return the type of graph, here ifft
        """
        return "ifft"

    def plot(self):
        """ Plot the inverse fft of signals.
        First calculate the inverse fft of each signal
        and then call the parent function
        """
        # Save signals
        origsigs = self.sigs
        self.sigs = {}
        # Compute FFT for all signals
        for sn, s in origsigs.iteritems():
            # Check whether ref sig is Freq
            s2 = Signal(s)
            if s.getref().getname() != "Freq":
                print "Warning : ref sig of", s.getname() ,"is not 'Freq'.\
 I hope you know what you do !"
            # Do a inverse fft
            y = numpy.fft.ifft(s.getpts())
            y = y[0:int(len(y)/2)-1]
            s2.setpts(y)
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.getref().getpts()[1]\
                                      - s.getref().getpts()[0]) \
                                  * len(s.getref().getpts())))
            s2.setref(Signal("Time", None, "s"))
            s2.getref().setpts(x)
            self.sigs[sn] = s2

        self.xunit = "s"
        self.xaxis = "Time"
        Graph.plot(self)

        # Restore signals
        self.sigs = origsigs
        return
