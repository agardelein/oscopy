""" LogxGraph -- A graph with logscale on X axis only

Class LogxGraph -- Draw graph with logscale on X axis only

   methods:
   setaxes()
      Set the X scale in log mode, and Y scale in lin mode

   gettype()
      Return the graph type, "logx"
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
