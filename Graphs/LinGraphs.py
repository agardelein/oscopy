""" A graph with linear scale on X and Y axis

Class LinGraph -- Draw graph with linear scale on X and Y axis

   methods:
   gettype()
      Return the mode of the graph "linear"

Class XYGraph -- Draw a xy graph using signals pairs
   methods:
   gettype()
      Return the mode of the graph "linear"
"""

import Graph
import pylab

class LinGraph(Graph.Graph):
    def gettype(self):
        """ Return 'linear', the type of the graph
        """
        return "linear"

# class XYGraph(Graph.Graph):
#     def gettype(self):
#         """ Return 'xy', the type of the graph
#         """
#         return 'xy'

#     def insert(self, sigs = {}):
#         """ Insert signals by pairs
#         """
