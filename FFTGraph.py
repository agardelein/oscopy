""" A graph with FFT or inverse FFT

Class FFTGraph -- Do an fft when inserting signals

   methods:
   insert(sigs)
      Add signals to the graph, do an fft

Class IFFTGraph -- Do an inverse fft when inserting signals

   methods:
   insert(sigs)
      Add signals to the graph, do an inverse fft

"""
from Graph import *
from Signal import *

class FFTGraph(Graph):
    
    def insert(self, sigs):
        """ Add a list of signals to the graph
        For each one, check whether the ref sig is Time,
        do a fft of the sig and change the ref sig from
        Time to Freq, then add it by calling Graph.insert()
        """
        mysigs = {}
        for s in sigs.itervalues():
            s2 = Signal(s)
            # Check whether ref sig is Time
            if s.ref.name != "Time":
                print "Warning : ref sig of", s.name ,"is not 'Time'.\
 I hope you know what you do !"
            # Do a fft
            y = fft(s.pts)
            y = y[0:int(len(y)/2)-1]
            s2.pts = y
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.ref.pts[1] - s.ref.pts[0]) \
                                  * len(s.ref.pts)))
            s2.ref.pts = x
            s2.ref.name = "Freq"
            s2.ref.unit = "Hz"
            mysigs[s2.name] = s2

        # Insert sigs into siglist
        return Graph.insert(self, mysigs)    

class IFFTGraph(Graph):
    def insert(self, sigs):
        """ Add a list of signals to the graph
        For each one, check whether the ref sig is Freq,
        do an inverse fft of the sig and change the ref sig from
        Freq to Time, then add it by calling Graph.insert()
        """
        mysigs = {}
        for s in sigs.itervalues():
            # Check whether ref sig is Freq
            s2 = Signal(s)
            if s.ref.name != "Freq":
                print "Warning : ref sig of", s.name ,"is not 'Freq'.\
 I hope you know what you do !"
            # Do a fft
            y = ifft(s.pts)
            y = y[0:int(len(y)/2)-1]
            s2.pts = y
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.ref.pts[1] - s.ref.pts[0]) \
                                  * len(s.ref.pts)))
            s2.ref.pts = x
            s2.ref.name = "Time"
            s2.ref.unit = "s"
            mysigs[s2.name] = s2

        # Insert sigs into siglist
        return Graph.insert(self, mysigs)    
