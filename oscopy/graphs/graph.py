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

   signals()
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
from matplotlib.pyplot import Axes as mplAxes
from matplotlib import rc
from cursor import Cursor

factors_to_names = {-18: ("a", 'atto'), -15:("f", 'femto'),
                 -12:("p", 'pico'), -9:("n", 'nano'),
                 -6:("u", 'micro'), -3:("m", 'milli'),
                 0:("",'(no scaling)'), 3:("k",'kilo'),
                 6:("M", 'mega'), 9:("G",'giga'),
                 12:("T", 'Tera'), 15:("P",'peta'),
                 18:("E", 'exa'), -31416:('auto', '(auto)')}

abbrevs_to_factors = {'E':18, 'P':15, 'T':12, 'G':9, 'M':6, 'k':3, '':0,
                     'a':-18, 'f':-15, 'p':-12, 'n':-9, 'u':-6, 'm':-3,
                      'auto':-31416}

names_to_factors = {'exa':18, 'peta':15, 'tera':12, 'giga':9, 'mega':6,
                    'kilo':3, '(no scaling)':0, 'atto':-18, 'femto':-15,
                    'pico':-12, 'nano':-9, 'micro':-6, 'milli':-3,
                    '(auto)':-31416}


class Graph(mplAxes):
    def __init__(self, fig, rect, sigs={}, **kwargs):
        """ Create a graph
        If signals are provided, fill in the graph otherwise the graph is empty
        Signals are assumed to exist and to be valid
        If first argument is a Graph, then copy things
        """
        mplAxes.__init__(self, fig, rect, **kwargs)
        self._sigs = {}

        if isinstance(sigs, Graph):
            mysigs = {}
            mysigs = sigs.sigs.copy()
            self._xrange = sigs.xrange
            self._yrange = sigs.yrange
            self._cursors = {"horiz": [None, None], "vert": [None, None]}
            self._txt = None
            self._scale_factors = sigs.scale_factors
            self._signals2lines = sigs._signals2lines.copy()
            self.insert(mysigs)
        else:
            self._xaxis = ""
            self._yaxis = ""
            self._xunit = ""
            self._yunit = ""
            self._xrange = []
            self._yrange = []
            # Cursors values, only two horiz and two vert but can be changed
            self._cursors = {"horiz":[None, None], "vert":[None, None]}
            self._txt = None
            self._scale_factors = [None, None]
            self._signals2lines = {}
            self.insert(sigs)

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
        rejected = {}
        for sn, s in sigs.iteritems():
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
                x = s.ref.data * pow(10, fx)
                y = s.data * pow(10, fy)
                line, = self.plot(x, y, label=sn)
                self._signals2lines[sn] = line
                self._draw_cursors()
                self._print_cursors()
                self.legend()
            else:
                if s.ref.name == self._xaxis and s.unit == self._yunit and\
                        not self._sigs.has_key(s.name):
                    # Add signal
                    self._sigs[sn] = s
                    fx, l = self._find_scale_factor("X")
                    fy, l = self._find_scale_factor("Y")
                    x = s.ref.data * pow(10, fx)
                    y = s.data * pow(10, fy)
                    line, = self.plot(x, y, label=sn)
                    self._signals2lines[sn] = line
                    self.legend()
                else:
                    # Ignore signal
                    rejected[sn] = s
        return rejected

    def remove(self, sigs={}):
        """ Delete signals from the graph
        """
        for sn in sigs.iterkeys():
            if sn in self._sigs.keys():
                del self._sigs[sn]
                self._signals2lines[sn].remove()
                self.plot()
                self.legend()
                del self._signals2lines[sn]
        return len(self._sigs)

    def update_signals(self):
        """
        """
        for sn, s in self._sigs.iteritems():
            fx, l = self._find_scale_factor("X")
            fy, l = self._find_scale_factor("Y")
            x = s.ref.data * pow(10, fx)
            y = s.data * pow(10, fy)
            self._signals2lines[sn].set_xdata(x)
            self._signals2lines[sn].set_ydata(y)            
    
    def _find_scale_factor(self, a):
        """ Choose the right scale for data on axis a
        Return the scale factor (f) and a string with the label. (l)
        E.g. for data from 0.001 to 0.01 return 3 and "m" for milli-
        """
        if a == "X" and self._scale_factors[0] is not None:
            return self._scale_factors[0], factors_to_names[-self._scale_factors[0]][0]
        if a == "Y" and self._scale_factors[1] is not None:
            return self._scale_factors[1], factors_to_names[-self._scale_factors[1]][0]
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
        if factors_to_names.has_key(-f) and \
                ((self._xunit != "" and a == "X") or \
                     (self._yunit != "" and a != "X")):
            l = factors_to_names[-f][0]
        else:
            if f == 0:
                l = ""
            else:
                l = "10e" + str(-f) + " "
        return f, l

    def get_unit(self):
        """ Return the graph units """
        return self._xunit, self._yunit

    def set_unit(self, unit):
        """ Define the graph units. If only one argument is provided,
        set y axis, if both are provided, set both.
        """
        if isinstance(unit, tuple):
            if len(unit) == 1 or (len(unit) == 2 and not unit[1]):
                self._yunit = unit[0]
            elif len(unit) == 2 and unit[1]:
                self._xunit = unit[0]
                self._yunit = unit[1]
            else:
                assert 0, _("Invalid argument")
        else:
            assert 0, _("Invalid argument")

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
        mplAxes.set_xlabel(self, xl)
        mplAxes.set_ylabel(self, yl)
        

    def get_scale(self):
        """ Return the axes scale
        """
#        return self._FUNC_TO_SCALES[self._plotf]
        # Is there a better way?
        x = self.get_xscale()
        y = self.get_yscale()
        if x == "linear" and y == "linear":
            return "lin"
        elif x == "linear" and y == "log":
            return "logy"
        elif y == "linear":
            return "logx"
        else:
            return "loglog"

    def set_scale(self, scale):
        """ Set axes scale, either lin, logx, logy or loglog
        """
        SCALES_TO_STR = {"lin": ["linear", "linear"],\
                             "logx": ["log","linear"],\
                             "logy": ["linear", "log"],\
                             "loglog": ["log", "log"]}
        mplAxes.set_xscale(self, SCALES_TO_STR[scale][0])
        mplAxes.set_yscale(self, SCALES_TO_STR[scale][1])

    def get_range(self):
        """ Return the axes limits
        """
        self._xrange = mplAxes.get_xlim(self)
        self._yrange = mplAxes.get_ylim(self)
        return self._xrange, self._yrange

    def set_range(self, arg="reset"):
        """ Set axis range
        Form 1: set_range("reset")                  delete range specs
        Form 2: set_range(("x", [xmin, xmax]))      set range for x axis
                set_range(("y", [ymin, ymax]))      set range for y axis
        Form 3: set_range([xmin, xmax, ymin, ymax]) set range for both axis
        """
        if arg == "reset":
            # Delete range specs
            self._xrange = []
            self._yrange = []
        elif isinstance(arg, list) and len(arg) == 4:
            self._xrange = [arg[0], arg[1]]
            self._yrange = [arg[2], arg[3]]            
        elif isinstance(arg, tuple):
            if len(arg) == 2 and isinstance(arg[0], str):
                if arg[0] == "x" and isinstance(arg[1], list) and\
                        len(arg[1]) == 2:
                    self._xrange = arg[1]
                elif arg[0] == "y" and isinstance(arg[1], list) and\
                        len(arg[1]) == 2:
                    self._yrange = arg[1]
        else:
            assert 0, _("Unrecognized argument")

        if len(self._xrange) == 2:
            mplAxes.set_xlim(self, self._xrange[0], self._xrange[1])
        if len(self._yrange) == 2:
            mplAxes.set_ylim(self, self._yrange[0], self._yrange[1])
        
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
            self._cursors[ctype][num].draw(self)
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
                    c.draw(self, ct.index(c))

    def _set_cursor(self, ctype, num, val):
        """ Add a cursor to the graph
        """
        if ctype in ["horiz", "vert"]:
            if num >= 0 and num < 2:
                # Just handle two cursor
                self._cursors[ctype][num] = Cursor(val, ctype)
                self._cursors[ctype][num].draw(self, num)
            else:
                assert 0, _("Invalid cursor number")
        else:
            assert 0, _("Invalid cursor type")

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

        if self._txt is None or not self._txt.axes == self:
            # Add text to graph
            rc('font', family='monospace')
            self._txt = self.text(0.02, 0.1, "",\
                                        transform=self.transAxes,\
                                        axes=self)
            self._txt.set_size(0.75 * self._txt.get_size())
        # Update text
        self._txt.set_text("%s\n%s" % (txt["horiz"], txt["vert"]))

    @property
    def signals(self):
        """ Return a list of the signal names
        """
        return self._sigs

    @property
    def type(self):
        """ Return a string with the type of the graph
        To be overloaded by derived classes.
        """
        return

    @property
    def axis_names(self):
        """Return the axis name"""
        return [self._xaxis, self._yaxis]

    def get_scale_factors(self):
        """Return the scane factors names"""
        fx, lx = self._find_scale_factor('X')
        fy, ly = self._find_scale_factor('Y')
        return [-fx, -fy]

    def set_scale_factors(self, x_factor, y_factor):
        old_fx, lx = self._find_scale_factor('X')
        old_fy, ly = self._find_scale_factor('Y')
        if x_factor is not None:
            self._scale_factors[0] = -x_factor
        else:
            self._scale_factors[0] = x_factor
        if y_factor is not None:
            self._scale_factors[1] = -y_factor
        else:
            self._scale_factors[1] = y_factor
        fx, lx = self._find_scale_factor('X')
        fy, ly = self._find_scale_factor('Y')
        xr, yr = self.get_range()
        self.set_range([xr[0] * pow(10, fx - old_fx),
                        xr[1] * pow(10, fx - old_fx),
                        yr[0] * pow(10, fy - old_fy),
                        yr[1] * pow(10, fy - old_fy)])
        self.update_signals()
        self.set_unit((self._xunit, self._yunit))

    unit = property(get_unit, set_unit)
    scale = property(get_scale, set_scale)
    range = property(get_range, set_range)
    scale_factors = property(get_scale_factors, set_scale_factors)
