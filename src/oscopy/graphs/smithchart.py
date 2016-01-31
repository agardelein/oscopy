from .graph import Graph
from matplotlib.projections.polar import PolarAxes
from smithplot.smithaxes import *

# https://en.wikipedia.org/wiki/Smith_chart
# http://www.mathworks.com/examples/rftoolbox/553-writing-a-touchstone-reg-file
# https://github.com/vMeijin/pySmithPlot

class SmithChart(Graph, SmithAxes):
    """ Class PolarGraph -- Draw graph with Polar scale on X and Y axis
    """
    def __init__(self, fig, rect, sigs={}, **kwargs):
        """ Create a graph
        If signals are provided, fill in the graph otherwise the graph is empty
        Signals are assumed to exist and to be valid
        If first argument is a Graph, then copy act as a copy constructor

        Parameters
        ----------
        fig: matplotlib.figure.Figure
        Figure where to build the Graph

        rect: array of 4 floats
        Coordinates of the Graph

        sigs: dict of Signals
        List of Signals to insert once the Graph instanciated

        See also matplotlib.pyplot.Axes for list of keyword arguments

        Returns
        -------
        self: Graph
        The Graph instanciated
        """
        SmithAxes.__init__(self, fig, rect, **kwargs)
        Graph.__init__(self, fig, rect, **kwargs)
        self._sigs = {}

        if isinstance(sigs, Graph):
            mysigs = {}
            mysigs = sigs.signals.copy()
            (self._xrange, self._yrange) = sigs.get_range()
            self._cursors = {"horiz": [None, None], "vert": [None, None]}
            self._txt = None
            self._scale_factors = sigs._scale_factors
            self._signals2lines = sigs._signals2lines.copy()
            self.insert(mysigs)
        else:
            self._xaxis = ""
            self._yaxis = ""
            self._xunit = ""
            self._yunit = ""
            self._xrange = [0, 1]
            self._yrange = [0, 1]
            # Cursors values, only two horiz and two vert but can be changed
            self._cursors = {"horiz":[None, None], "vert":[None, None]}
            self._txt = None
            self._scale_factors = [None, None]
            self._signals2lines = {}
            self.insert(sigs)
            
    @property
    def type(self):
        """ Return 'Polar', the type of the graph

        Parameter
        ---------
        None

        Returns
        -------
        string:
        The type of the graph
        """
        return "smith"

    def insert(self, sigs={}):
        """ Add a list of signals into the graph
        The first signal to be added defines the abscisse.
        The remaining signals to be added must have the same abscisse name,
        otherwise they are silently ignored.
        Returns the list of ignored signals

        Parameters
        ----------
        sigs: dict of Signals
        List of Signals to be inserted in the Graph

        Returns
        -------
        rejected: dict of Signals
        List of Signals that where not inserted
        """
        rejected = {}
        for sn, s in sigs.items():
            if not self._sigs:
                # First signal, set_ the abscisse name and add signal
                self._xaxis = s.ref.name
                self._xunit = s.ref.unit
                self._yaxis = _("Signals")  # To change
                self._yunit = s.unit
                self._sigs[sn] = s
                self.set_unit((self._xunit, self._yunit))
                fx, l = self._find_scale_factor("X")
                fy, l = self._find_scale_factor("Y")
                x = s.data.real
                y = s.data.imag
                line, = self.plot(x, y, label=sn)
                self._signals2lines[sn] = line
                self._draw_cursors()
                self._print_cursors()
                self.legend()
            else:
                if s.ref.name == self._xaxis and s.unit == self._yunit and\
                        s.name not in self._sigs:
                    # Add signal
                    self._sigs[sn] = s
#                    fx, l = self._find_scale_factor("X")
#                    fy, l = self._find_scale_factor("Y")
                    x = s.data.real
                    y = s.data.imag
                    line, = self.plot(x, y, label=sn)
                    self._signals2lines[sn] = line
                    self.legend()
                else:
                    # Ignore signal
                    rejected[sn] = s
        return rejected
