""" Graph Handler

A graph consist of several signals that share the same abscisse,
and plotted according a to mode, which is currently scalar.

Signals are managed as a dict, where the key is the signal name.

In a graph, signals with a different sampling, but with the same abscisse
can be plotted toget_her.

Handle a cursor dict, for convenience limited to two horizontal
and two vertical, limit can be removed. 

sn: signal name
s : signal

Class Graph -- Handle the representation of a list of signals

   methods:
   __init__(sigs)
      Create a graph and fill it with the sigs

   __str__()
      Return a string with the list of signals, and abscisse name

   insert(sigs)
      Add signal list to the graph, set_ the abscisse name

   remove(sigs)
      Delete signals from the graph

   plot()
      Plot the graph

   get_sigs()
      Return a list of the signal names

   type()
      Return a string with the type of graph, to be overloaded.

   set_units()
      Define the axis unit

   set_scale()
      Set plot axis scale (lin, logx, logy, loglog)

   set_range()
      Set plot axis range
"""

import matplotlib.pyplot as plt
from matplotlib import rc
from Cursor import Cursor

class Graph(object):
    def __init__(self, sigs={}):
        """ Create a graph
        If signals are provided, fill in the graph otherwise the graph is empty
        Signals are assumed to exist and to be valid
        If first argument is a Graph, then copy things
        """
        self._sigs = {}
        if isinstance(sigs, Graph):
            # Warn on some conversion that may lead to nasty things
            if (sigs.type.find('fft') == 0 \
                    and self.type.find('ifft') == 0) \
                    or (sigs.type.find('ifft') == 0 \
                            and self.type.find('fft') == 0):
                print "Warning: fft <=> ifft conversions and vice versa \
may lead to uncertain results"

            mysigs = {}
            mysigs = sigs.sigs.copy()
            self.insert(mysigs)
            self._plotf = sigs.plotf
            self._xrange = sigs.xrange
            self._yrange = sigs.yrange
            self._ax = sigs.ax
            self._cursors = {"horiz": [None, None], "vert": [None, None]}
            self._txt = None
        else:
            self._xaxis = ""
            self._yaxis = ""
            self._xunit = ""
            self._yunit = ""
            self._xrange = []
            self._yrange = []
            self.insert(sigs)
            self._plotf = plt.plot
            self._ax = None
            # Cursors values, only two horiz and two vert but can be changed
            self._cursors = {"horiz":[None, None], "vert":[None, None]}
            self._txt = None

    def __str__(self):
        """ Return a string with the type and the signal list of the graph
        """
        a = "(" + self.type + ") "
        for sn in self._sigs.keys():
            a = a + sn + " "
        return a

    def insert(self, sigs={}):
        """ Add a list of signals into the graph
        The first signal to be added defines the abscisse.
        The remaining signals to be added must have the same abscisse name,
        otherwise they are ignored
        """
        for sn, s in sigs.iteritems():
            if not self._sigs:
                # First signal, set_ the abscisse name and add signal
                self._xaxis = s.ref.name
                self._xunit = s.ref.unit
                self._yaxis = "Signals"  # To change
                self._yunit = s.unit
                self._sigs[sn] = s
            else:
                if s.ref.name == self._xaxis:
                    # Add signal
                    self._sigs[sn] = s
                else:
                    # Ignore signal
                    print "Not the same ref:", sn, "-", self._xaxis,"-"
        return len(self._sigs)

    def remove(self, sigs={}):
        """ Delete signals from the graph
        """
        for sn in sigs.iterkeys():
            if sn in self._sigs.keys():
                del self._sigs[sn]
        return len(self._sigs)

    def plot(self, ax=None):
        """ Plot the graph in Matplotlib Axes instance ax
        Each signal is plotted regarding to its proper abscisse.
        In this way, signals with a different sampling can be plotted toget_her.
        The x axis is labelled with the abscisse name of the graph.
        """
        if not self._sigs:
            return
        # Prepare labels
        xl = self._xaxis
        if not self._xunit:
            xu = "a.u."
        else:
            xu = self._xunit
        fx, l = self._find_scale_factor("X")
        xl = xl + " (" + l + xu + ")"
        yl = self._yaxis
        if not self._yunit:
            yu = "a.u."
        else:
            yu = self._yunit
        fy, l = self._find_scale_factor("Y")
        yl = yl + " (" + l + yu + ")"
        
        # Plot the signals
        ax.hold(True)
        for sn, s in self._sigs.iteritems():
            # Scaling factor
            x = s.ref.data * pow(10, fx)
            y = s.data * pow(10, fy)
            try:
                self._plotf(x, y, label=sn)
            except OverflowError, e:
                print "OverflowError in plot:", e.message, ", log(0) somewhere ?"
                ax.hold(False)
                ax.set_xlabel(xl)
                ax.set_ylabel(yl)
                return
        ax.hold(False)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        if len(self._xrange) == 2:
            ax.set_xlim(self._xrange[0], self._xrange[1])
        if len(self._yrange) == 2:
            ax.set_ylim(self._yrange[0], self._yrange[1])
        ax.legend()

        self._ax = ax
        self._draw_cursors()
        self._print_cursors()

    def get_sigs(self):
        """ Return a list of the signal names
        """
        for sn in self._sigs:
            yield sn

    @property
    def type(self):
        """ Return a string with the type of the graph
        To be overloaded by derived classes.
        """
        return
    
    def _find_scale_factor(self, a):
        """ Choose the right scale for data on axis a
        Return the scale factor (f) and a string with the abbrev. (l)
        """
        scnames = {-18: "a", -15:"f", -12:"p", -9:"n", -6:"u", -3:"m", \
            0:"", 3:"k", 6:"M", 9:"G", 12:"T", 15:"P", 18:"E"}

        # Find the absolute maximum of the data
        mxs = []
        mns = []

        for s in self._sigs.itervalues():
            if a == "X":
                mxs.append(max(s.ref.data))
                mns.append(min(s.ref.data))
            else:
                mxs.append(max(s.data))
                mns.append(min(s.data))
        mx = abs(max(mxs))
        mn = abs(min(mns))
        mx = max(mx, mn)

        # Find the scaling factor using the absolute maximum
        if abs(mx) > 1:
            fct = -3
        else:
            fct = 3
        f = 0
        while not (abs(mx * pow(10.0, f)) < 1000.0 \
                       and abs(mx * pow(10.0, f)) >= 1.0):
            f = f + fct
        if scnames.has_key(-f) and ((self._xunit != "" and a == "X") \
                or (self._yunit != "" and a != "X")):
            l = scnames[-f]
        else:
            if f == 0:
                l = ""
            else:
                l = "10e" + str(-f) + " "
        return f, l

    def set_unit(self, xu, yu=""):
        """ Define the graph units. If only one argument is provided,
        set_ y axis, if both are provided, set_ both.
        """
        if not yu:
            self._yunit = xu
        else:
            self._xunit = xu
            self._yunit = yu

    def set_scale(self, a):
        """ Set axes scale, either lin, logx, logy or loglog
        """
        if isinstance(a, str):
            if a == "lin":
                self._plotf = plt.plot
            elif a == "logx":
                self._plotf = plt.semilogx
            elif a == "logy":
                self._plotf = plt.semilogy
            elif a == "loglog":
                self._plotf = plt.loglog

    def set_range(self, a1="reset", a2=None, a3=None, a4=None):
        """ Set axis range
        Form 1: set_range("reset")                delete range specs
        Form 2: set_range("x", xmin, xmax)        set_ range for x axis
                set_range("y", ymin, ymax)        set_ range for y axis
        Form 3: set_range(xmin, xmax, ymin, ymax) set_ range for both axis
        """
        if isinstance(a1, str) and a1 == "reset":
            # Delete range specs
            self._xrange = []
            self._yrange = []
        if a4 is None:
            # Set either x or y range
            if a1 == 'x':
                self._xrange = [a2, a3]
            elif a1 == 'y':
                self._yrange = [a2, a3]
        else:
            # Set range for both axis
            self._xrange = [a1, a2]
            self._yrange = [a3, a4]
        
    def toggle_cursors(self, ctype="", num=None, val=None):
        """ Toggle the cursors in the graph
        Call canvas.draw() shoud be called after to update the figure
        cnt: cursor type
        """
        if not ctype or num is None or val is None:
            return

        if not ctype in ["horiz", "vert"]:
            return
        if num >= len(self._cursors[ctype]):
            return
        if val is None:
            return
        if self._cursors[ctype][num] is None:
            self._set_cursor(ctype, num, val)
        else:
            self._cursors[ctype][num].value = val
            self._cursors[ctype][num].set_visible()
            self._cursors[ctype][num].draw(self._ax)
        self._print_cursors()
        fx, lx = self._find_scale_factor("X")
        fy, ly = self._find_scale_factor("Y")

    def _draw_cursors(self):
        """ Draw the cursor lines on the graph
        Called at the end of plot()
        """
        fx, lx = self._find_scale_factor("X")
        fy, ly = self._find_scale_factor("Y")
        l = {"horiz": ly, "vert": lx}
        txt = {"horiz": "", "vert": ""}
        for t, ct in self._cursors.iteritems():
            for c in ct:
                if c is not None:
                    c.draw(self._ax, ct.index(c))

    def _set_cursor(self, ctype, num, val):
        """ Add a cursor to the graph
        """
        if ctype in ["horiz", "vert"]:
            if num >= 0 and num < 2:
                # Just handle two cursor
                self._cursors[ctype][num] = Cursor(val, ctype)
                self._cursors[ctype][num].draw(self._ax, num)

    def _print_cursors(self):
        """ Print cursors values on the graph
        If both cursors are set_, print difference (delta)
        """
        fx, lx = self._find_scale_factor("X")
        fy, ly = self._find_scale_factor("Y")
        l = {"horiz": ly, "vert": lx}
        u = {"horiz": self._yunit, "vert": self._xunit}
        txt = {"horiz": "", "vert": ""}
        # Preapre string for each cursor type (i.e. "horiz" and "vert")
        for t, cl in self._cursors.iteritems():
            for c in cl:
                if c is not None and c.visible:
                    # Add cursors value to text
                    txt[t] += " %d: %8.3f %2s%-3s" \
                        % (cl.index(c) + 1, float(c.value), l[t], u[t])
            if not None in cl and cl[0].visible and cl[1].visible:
                # Add cursors difference (delta)
                txt[t] += " d%s: %8.3f %2s%-3s"\
                    % (u[t], float(cl[1].value - cl[0].value),\
                           l[t], u[t])

        if self._txt is None or not self._txt.axes == self._ax:
            # Add text to graph
            rc('font', family='monospace')
            self._txt = self._ax.text(0.02, 0.1, "",\
                                        transform=self._ax.transAxes,\
                                        axes=self._ax)
            self._txt.set_size(0.75 * self._txt.get_size())
        # Update text
        self._txt.set_text("%s\n%s" % (txt["horiz"], txt["vert"]))

    @property
    def ax(self):
        """ Return the Matplotlib axe
        """
        return self._ax
