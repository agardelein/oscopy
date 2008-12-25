""" LogGraphs -- A graph with logscale for X, Y or both

Class LogxGraph -- Draw graph with logscale for X axis only

   methods:
   setaxes()
      Set the X scale in log mode, and Y scale in lin mode

   gettype()
      Return the graph type, "logx"

Class LogyGraph -- Draw graph with logscale for Y axis only

   methods:
   setaxes()
      Set the Y scale in log mode, and X scale in lin mode

   gettype()
      Return the graph type, "logy"

Class LoglogGraph -- Draw graph with logscale for X and y axis

   methods:
   setaxes()
      Set the X and Y scales in log mode

   gettype()
      Return the graph type, "loglog"
"""

from BaseGraph import *

class LogxGraph(BaseGraph):
    def setaxes(self):
        """ The x axis is log, the y axis is linear
        """
        xscale("log")
        yscale("linear")

    def gettype(self):
        """ Return 'linear', the type of the graph
        """
        return "logx"

class LogyGraph(BaseGraph):
    def setaxes(self):
        """ The y axis is log, the x axis is linear
        """
        xscale("linear")
        yscale("log")

    def gettype(self):
        """ Return 'logy', the type of the graph
        """
        return "logy"

class LoglogGraph(BaseGraph):
    def setaxes(self):
        """ The x and y axis are both log
        """
        xscale("log")
        yscale("log")

    def gettype(self):
        """ Return 'loglog', the type of the graph
        """
        return "loglog"
