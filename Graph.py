from Axe import Axe
import matplotlib.pyplot as plt
from pylab import *

class Graph:
#    mode = "scal"
#    axex = 0
#    axey = 0
#    sigs = {}
#    xaxis = ""

    # Create axis, and fill them with data
    def __init__(self, sigs = None, mode = "scal"):
        # Here signals do exist and are valid
        self.mode = mode
        self.sigs = {}
        self.xaxis = ""
        if sigs == None:
            return
        else:
            self.add(sigs)
            return

    def add(self, sigs = None):
        if sigs == None:
            return
        for s in sigs:
            if len(self.sigs) == 0:
                self.xaxis = s.ref.name
                self.sigs[s.name] = s
            else:
                if s.ref.name == self.xaxis:
                    self.sigs[s.name] = s
                else:
                    print "Not the same ref:", s.name, "-", self.xaxis,"-"

    def setg(self, sigs = None):
        self.sigs = {}
        self.xaxis = ""
        self.add(sigs)

    def plot(self):
        hold(True)
        for n, s in self.sigs.iteritems():
            x = s.ref.pts
            y = s.pts
            plot(x, y)
        hold(False)
        xlabel(self.xaxis)

    def __str__(self):
        a = self.mode + " "
        for n, s in self.sigs.iteritems():
            a = a + n
            a = a + " "
        return a
