""" A graph with linear scale on X and Y axis

Class LinGraph -- Draw graph with linear scale on X and Y axis

   methods:
   get_type()
      Return the mode of the graph "linear"

Class XYGraph -- Draw a xy graph using signals pairs
   methods:
   get_type()
      Return the mode of the graph "linear"
"""

from Graph import Graph
import pylab

class LinGraph(Graph):
    def get_type(self):
        """ Return 'linear', the type of the graph
        """
        return "linear"

# class XYGraph(Graph.Graph):
#     def get_type(self):
#         """ Return 'xy', the type of the graph
#         """
#         return 'xy'

#     def insert(self, sigs = {}):
#         """ Insert signals by pairs
#         """
