from graph import Graph

class LinGraph(Graph):
    """ Class LinGraph -- Draw graph with linear scale on X and Y axis
    """
    @property
    def type(self):
        """ Return 'linear', the type of the graph

        Parameter
        ---------
        None

        Returns
        -------
        string:
        The type of the graph
        """
        return "linear"

# class XYGraph(Graph.Graph):
#     """ Class XYGraph -- Draw a xy graph using signals pairs
#     """
#     def get_type(self):
#         """ Return 'xy', the type of the graph
#         """
#         return 'xy'

#     def insert(self, sigs = {}):
#         """ Insert signals by pairs
#         """
