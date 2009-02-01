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
import Graph
import Signal 
import pylab

class FFTGraph(Graph.Graph):
    
    def insert(self, sigs):
        """ Add a list of signals to the graph
        For each one, check whether the ref sig is Time,
        do a fft of the sig and change the ref sig from
        Time to Freq, then add it by calling Graph.insert()
        """
        mysigs = {}
        for s in sigs.itervalues():
            s2 = Signal.Signal(s)
            # Check whether ref sig is Time
            if s.getref().getname() != "Time":
                print "Warning : ref sig of", s.getname() ,"is not 'Time'.\
 I hope you know what you do !"
            # Do a fft
            y = pylab.fft(s.getpts())
            y = y[0:int(len(y)/2)-1]
            s2.setpts(y)
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.getref().getpts()[1]\
                                      - s.getref().getpts()[0])\
                                  * len(s.getref().getpts())))
            s2.setref(Signal.Signal("Freq", None, "Hz"))
            s2.getref().setpts(x)
            mysigs[s2.getname()] = s2

        # Insert sigs into siglist
        return Graph.Graph.insert(self, mysigs)    

class IFFTGraph(Graph.Graph):
    def insert(self, sigs):
        """ Add a list of signals to the graph
        For each one, check whether the ref sig is Freq,
        do an inverse fft of the sig and change the ref sig from
        Freq to Time, then add it by calling Graph.insert()
        """
        mysigs = {}
        for s in sigs.itervalues():
            # Check whether ref sig is Freq
            s2 = Signal.Signal(s)
            if s.getref().getname() != "Freq":
                print "Warning : ref sig of", s.getname() ,"is not 'Freq'.\
 I hope you know what you do !"
            # Do a inverse fft
            y = pylab.ifft(s.getpts())
            y = y[0:int(len(y)/2)-1]
            s2.setpts(y)
            # Change the ref sig from Time to Freq
            x = []
            for i in range(0, len(y)):
                x.append(i / (abs(s.getref().getpts()[1]\
                                      - s.getref().getpts()[0]) \
                                  * len(s.getref().getpts())))
            s2.setref(Signal.Signal("Time", None, "s"))
            s2.getref().setpts(x)
            mysigs[s2.getname()] = s2

        # Insert sigs into siglist
        return Graph.Graph.insert(self, mysigs)    
