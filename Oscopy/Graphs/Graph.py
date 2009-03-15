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

   get_type()
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
import types
from Cursor import Cursor

class Graph:
    def __init__(self, sigs = {}):
        """ Create a graph
        If signals are provided, fill in the graph otherwise the graph is empty
        Signals are assumed to exist and to be valid
        If first argument is a Graph, then copy things
        """
        self.sigs = {}
        if isinstance(sigs, Graph):
            # Warn on some conversion that may lead to nasty things
            if (sigs.get_type().find('fft') == 0 \
                    and self.get_type().find('ifft') == 0) \
                    or (sigs.get_type().find('ifft') == 0 \
                            and self.get_type().find('fft') == 0):
                print "Warning: fft <=> ifft conversions and vice versa \
may lead to uncertain results"

            mysigs = {}
            mysigs = sigs.sigs.copy()
            self.insert(mysigs)
            self.plotf = sigs.plotf
            self.xrange = sigs.xrange
            self.yrange = sigs.yrange
            self.ax = sigs.ax
            self.cursors = {"horiz": [None, None], "vert": [None, None]}
            self.txt = None
        else:
            self.xaxis = ""
            self.yaxis = ""
            self.xunit = ""
            self.yunit = ""
            self.xrange = []
            self.yrange = []
            self.insert(sigs)
            self.plotf = plt.plot
            self.ax = None
            # Cursors values, only two horiz and two vert but can be changed
            self.cursors = {"horiz": [None, None], "vert": [None, None]}
            self.txt = None

    def __str__(self):
        """ Return a string with the type and the signal list of the graph
        """
        a = "(" + self.get_type() + ") "
        for sn in self.sigs.keys():
            a = a + sn + " "
        return a

    def insert(self, sigs = {}):
        """ Add a list of signals into the graph
        The first signal to be added defines the abscisse.
        The remaining signals to be added must have the same abscisse name,
        otherwise they are ignored
        """
        for sn, s in sigs.iteritems():
            if len(self.sigs) == 0:
                # First signal, set_ the abscisse name and add signal
                self.xaxis = s.get_ref().get_name()
                self.xunit = s.get_ref().get_unit()
                self.yaxis = "Signals"  # To change
                self.yunit = s.get_unit()
                self.sigs[sn] = s
            else:
                if s.get_ref().get_name() == self.xaxis:
                    # Add signal
                    self.sigs[sn] = s
                else:
                    # Ignore signal
                    print "Not the same ref:", sn, "-", self.xaxis,"-"
        return len(self.sigs)

    def remove(self, sigs = {}):
        """ Delete signals from the graph
        """
        for sn in sigs.iterkeys():
            if sn in self.sigs.keys():
                del self.sigs[sn]
        return len(self.sigs)

    def plot(self, ax = None):
        """ Plot the graph in Matplotlib Axes instance ax
        Each signal is plotted regarding to its proper abscisse.
        In this way, signals with a different sampling can be plotted toget_her.
        The x axis is labelled with the abscisse name of the graph.
        """
        if len(self.sigs) == 0:
            return
        # Prepare labels
        xl = self.xaxis
        if self.xunit == "":
            xu = "a.u."
        else:
            xu = self.xunit
        fx, l = self.find_scale_factor("X")
        xl = xl + " (" + l + xu + ")"
        yl = self.yaxis
        if self.yunit == "":
            yu = "a.u."
        else:
            yu = self.yunit
        fy, l = self.find_scale_factor("Y")
        yl = yl + " (" + l + yu + ")"
        
        # Plot the signals
        ax.hold(True)
        for sn, s in self.sigs.iteritems():
            # Scaling factor
            # The hard way...
            x = []
            for i in s.get_ref().get_data():
                x.append(i * pow(10, fx))
            # The hard way, once again
            y = []
            for i in s.get_data():
                y.append(i * pow(10, fy))
            try:
                self.plotf(x, y, label=sn)
            except OverflowError, e:
                print "OverflowError in plot:", e.message, ", log(0) somewhere ?"
                ax.hold(False)
                ax.set_xlabel(xl)
                ax.set_ylabel(yl)
                return
        ax.hold(False)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        if len(self.xrange) == 2:
            ax.set_xlim(self.xrange[0], self.xrange[1])
        if len(self.yrange) == 2:
            ax.set_ylim(self.yrange[0], self.yrange[1])
        ax.legend()

        self.ax = ax
        self.draw_cursors()
        self.print_cursors()

    def get_sigs(self):
        """ Return a list of the signal names
        """
        for sn in self.sigs:
            yield sn

    def get_type(self):
        """ Return a string with the type of the graph
        To be overloaded by derived classes.
        """
        return
    
    def find_scale_factor(self, a):
        """ Choose the right scale for data on axis a
        Return the scale factor (f) and a string with the abbrev. (l)
        """
        scnames = {-18: "a", -15:"f", -12:"p", -9:"n", -6:"u", -3:"m", \
            0:"", 3:"k", 6:"M", 9:"G", 12:"T", 15:"P", 18:"E"}

        # Find the absolute maximum of the data
        mxs = []
        mns = []

        for s in self.sigs.itervalues():
            if a == "X":
                mxs.append(max(s.get_ref().get_data()))
                mns.append(min(s.get_ref().get_data()))
            else:
                mxs.append(max(s.get_data()))
                mns.append(min(s.get_data()))
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
        if scnames.has_key(-f) and ((self.xunit != "" and a == "X") \
                or (self.yunit != "" and a != "X")):
            l = scnames[-f]
        else:
            if f == 0:
                l = ""
            else:
                l = "10e" + str(-f) + " "
        return f, l

    def set_unit(self, xu, yu = ""):
        """ Define the graph units. If only one argument is provided,
        set_ y axis, if both are provided, set_ both.
        """
        if yu == "":
            self.yunit = xu
        else:
            self.xunit = xu
            self.yunit = yu

    def set_scale(self, a):
        """ Set axes scale, either lin, logx, logy or loglog
        """
        if type(a) == types.StringType:
            if a == "lin":
                self.plotf = plt.plot
            elif a == "logx":
                self.plotf = plt.semilogx
            elif a == "logy":
                self.plotf = plt.semilogy
            elif a == "loglog":
                self.plotf = plt.loglog

    def set_range(self, a1 = "reset_", a2 = None, a3 = None, a4 = None):
        """ Set axis range
        Form 1: set_range("reset_")                delete range specs
        Form 2: set_range("x", xmin, xmax)        set_ range for x axis
                set_range("y", ymin, ymax)        set_ range for y axis
        Form 3: set_range(xmin, xmax, ymin, ymax) set_ range for both axis
        """
        if type(a1) == types.StringType and a1 == "reset_":
            # Delete range specs
            self.xrange = []
            self.yrange = []
        if a4 == None:
            # Set either x or y range
            if a1 == 'x':
                self.xrange = [a2, a3]
            elif a1 == 'y':
                self.yrange = [a2, a3]
        else:
            # Set range for both axis
            self.xrange = [a1, a2]
            self.yrange = [a3, a4]
        
    def toggle_cursors(self, ctype = "", num = None, val = None):
        """ Toggle the cursors in the graph
        Call canvas.draw() shoud be called after to update the figure
        cnt: cursor type
        """
        if ctype == "" or num == None or val == None:
            return

        if not ctype in ["horiz", "vert"]:
            return
        if num >= len(self.cursors[ctype]):
            return
        if val == None:
            return
        if self.cursors[ctype][num] == None:
            self.set_cursor(ctype, num, val)
        else:
            self.cursors[ctype][num].set_value(val)
            self.cursors[ctype][num].set_visible()
            self.cursors[ctype][num].draw(self.ax)
        self.print_cursors()
        fx, lx = self.find_scale_factor("X")
        fy, ly = self.find_scale_factor("Y")

    def draw_cursors(self):
        """ Draw the cursor lines on the graph
        Called at the end of plot()
        """
        fx, lx = self.find_scale_factor("X")
        fy, ly = self.find_scale_factor("Y")
        l = {"horiz": ly, "vert": lx}
        txt = {"horiz": "", "vert": ""}
        for t, ct in self.cursors.iteritems():
            for c in ct:
                if not c == None:
                    c.draw(self.ax, ct.index(c))

    def set_cursor(self, ctype, num, val):
        """ Add a cursor to the graph
        """
        if ctype in ["horiz", "vert"]:
            if num >= 0 and num < 2:
                # Just handle two cursor
                self.cursors[ctype][num] = Cursor(val, ctype)
                self.cursors[ctype][num].draw(self.ax, num)

    def print_cursors(self):
        """ Print cursors values on the graph
        If both cursors are set_, print difference (delta)
        """
        fx, lx = self.find_scale_factor("X")
        fy, ly = self.find_scale_factor("Y")
        l = {"horiz": ly, "vert": lx}
        u = {"horiz": self.yunit, "vert": self.xunit}
        txt = {"horiz": "", "vert": ""}
        # Preapre string for each cursor type (i.e. "horiz" and "vert")
        for t, cl in self.cursors.iteritems():
            for c in cl:
                if not c == None and c.get_visible() == True:
                    # Add cursors value to text
                    txt[t] += " %d: %8.3f %2s%-3s" \
                        % (cl.index(c) + 1, float(c.get_value()), l[t], u[t])
            if not None in cl and cl[0].get_visible() and cl[1].get_visible():
                # Add cursors difference (delta)
                txt[t] += " d%s: %8.3f %2s%-3s"\
                    % (u[t], float(cl[1].get_value() - cl[0].get_value()),\
                           l[t], u[t])

        if self.txt == None or not self.txt.axes == self.ax:
            # Add text to graph
            rc('font', family='monospace')
            self.txt = self.ax.text(0.02, 0.1, "",\
                                        transform=self.ax.transAxes,\
                                        axes=self.ax)
            self.txt.set_size(0.75 * self.txt.get_size())
        # Update text
        self.txt.set_text("%s\n%s" % (txt["horiz"], txt["vert"]))
