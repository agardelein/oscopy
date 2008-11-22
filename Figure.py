from Graph import *
import matplotlib.pyplot as plt
from pylab import *

class Figure:
    graphs = []
    sigs = []

    def __init__(self, sigs = None):
        if sigs == None:
            return
        gr = Graph(sigs)
        self.graphs.append(gr)
        self.sigs.extend(sigs)

    def add(self):
        a = 0

    def delete(self):
        a = 0

    def update(self):
        a = 0

    def list(self):
        print "yo"
        
    def plot(self, sigs = None):
        if sigs != None:
            self.sigs = sigs
        print "figplot"
        hold(True)
        for s in self.sigs:
            x = s.ref.pts
            y = s.pts
            plot(x, y)
        hold(False)
        show()
        return
