""" A graph with FFT or inverse FFT

Class FFTGraph -- Do an fft when plotting

   methods:
   plot()
   Plot the fft of the signals

   get_type()
   Return "fft", the type of the graph

Class IFFTGraph -- Do an inverse fft when plotting signals

   methods:
   plot()
   Plot the inverse fft of signals

   get_type()
   Return "ifft", the type of the graph
"""
from Graph import Graph
from oscopy.Signal import Signal
import numpy.fft

class FFTGraph(Graph):

    def plot(self, ax = None):
        """ Plot the fft of signals.
        First calculate the fft of each signal
        and then call the parent function
        """
        # Save signals
        origsigs = self.sigs
        self.sigs = {}
        # Compute FFT for all signals
        for sn, s in origsigs.iteritems():
            s2 = Signal(sn, s.unit)
            # Check whether ref sig is Time
            if s.ref.name != "Time":
                print "Warning : ref sig of", s.name ,"is not 'Time'.\
 I hope you know what you do !"
            # Do a fft
            y = numpy.fft.fft(s.data)
            y = y[0:int(len(y)/2)-1]
            s2.data = y
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.ref.data[1]\
                                      - s.ref.data[0])\
                                  * len(s.ref.data)))
            s2.ref = Signal("Freq", "Hz")
            s2.ref.data = x
            self.sigs[sn] = s2

        self.xunit = "Hz"
        self.xaxis = "Freq"
        Graph.plot(self, ax)

        # Restore signals
        self.sigs = origsigs
        return

    def get_type(self):
        """ Return the type of graph, here fft
        """
        return "fft"

class IFFTGraph(Graph):
    def get_type(self):
        """ Return the type of graph, here ifft
        """
        return "ifft"

    def plot(self, ax = None):
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
            if s.ref.name != "Freq":
                print "Warning : ref sig of", s.name ,"is not 'Freq'.\
 I hope you know what you do !"
            # Do a inverse fft
            y = numpy.fft.ifft(s.data)
            y = y[0:int(len(y)/2)-1]
            s2.data = y
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.ref.data[1]\
                                      - s.ref.data[0]) \
                                  * len(s.ref.data)))
            s2.ref = Signal("Time", "s")
            s2.ref.data = x
            self.sigs[sn] = s2

        self.xunit = "s"
        self.xaxis = "Time"
        Graph.plot(self, ax)

        # Restore signals
        self.sigs = origsigs
        return
