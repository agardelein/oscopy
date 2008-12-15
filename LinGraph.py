""" A graph with linear scale on X and Y axis

Class LinGraph -- Draw graph with linear scale on X and Y axis

   methods:
   setaxes()
      Set the X and Y scale in linear mode

   gettype()
      Return the mode of the graph "linear"
"""

from BaseGraph import *

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
