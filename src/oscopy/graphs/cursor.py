class Cursor(object):
    """ Class Cursor -- Handle cursors in plots
A cursor is an horizontal or vertical line drawn across the plot,
depending on type, either "horiz" or "vert".
The line position depends on the value.
It can be visible or not.
It contains an alias to the Line2D object in the plot.

The purpose of this class is also to be derived to propose other types or
styles of cursors e.g. the ones used on modern scopes or spectrum analysers.

Properties
    value     location of the cursor
    visible   display the cursor when drawing its Graph
    type      cursor orientation (horiz, vert)
    """
    def __init__(self, val, type):
        """ Instanciate the Cursor values

        Parameters
        ----------
        val: float
        The position of the cursor on the Graph

        type: string, one of ['horiz', 'vert']
        The type of the Cursor. 'horiz' for an horizontal line drawn accross the
        graph, 'vert' for a vertical line.

        Returns
        -------
        Cursor:
        The instanciated object
        """
        self.set_value(val)
        self.set_visible(True)
        self._line = None # Line2D
        self.set_type(type)

    def draw(self, ax=None, num=0):
        """ Draw cursor on axis ax, num is the linestyle 0 for solid,
        non-zero for dashed

        Parameters
        ----------
        ax: Graph
        The Graph where to draw the cursor

        num: integer
        0 for solid, non-zero for dashed

        Returns
        -------
        Nothing
        """
        # Check whether cursor is within the axis limits
        if self._type == "horiz":
            lim = ax.get_ybound()
        elif self._type == "vert":
            lim = ax.get_xbound()
        else:
            return
        if self._value < lim[0] or self._value > lim[1]:
            # Outside axe limits, delete line and that's it
            self._line = None
            return

        # Cursor is within the limit
        if self._line is None or not self._line.get_axes() == ax:
            # Cursor do not exist on the graph, plot it
            ax.hold(True)
            if self._type not in ['horiz', 'vert']:
                return
            if num == 0:
                lt = "-"
            else:
                lt = "--"
            #self._line, = ax.plot(x, y, lt + "k")
            if self._type == 'horiz':
                self._line = ax.axhline(y=self._value, ls=lt, c='k')
            elif self._type == 'vert':
                self._line = ax.axvline(x=self._value, ls=lt, c='k')
            self._line.set_visible(self._visible)
            ax.hold(False)
        elif ax == self._line.get_axes():
            # Cursor already exist, just update visibility
            if self._type == 'horiz':
                self._line.set_ydata([self._value, self._value])
            elif self._type == 'vert':
                self._line.set_xdata([self._value, self._value])
            self._line.set_visible(self._visible)
        else:
            # Cursor exist already in this graph, nothing to do
            pass

    def get_type(self):
        """ Returns the type of the Cursor

        Parameter
        ---------
        None

        Returns
        -------
        string: one of ['horiz' or 'vert']
        The type of the Cursor
        """
        return self._type

    def get_value(self):
        """ Returns the location of the Cursor on the Graph

        Parameter
        ---------
        None

        Returns
        -------
        float
        The position of the cursor. For 'horiz' type, this is the 'Y' coordinate
        and for 'vert' type, this is the 'X' coordinate
        """
        return self._value

    def get_visible(self):
        """ Returns whether the Cursor is displayed or not

        Parameter
        ---------
        None

        Returns
        -------
        bool
        True if the cursor is displayed on the Graph
        """
        return self._visible

    def set_type(self, type=""):
        """ Set the type of the Cursor

        Parameter
        ---------
        type: string, one of  'horiz' or 'vert'
        The type of the Cursor

        Returns
        -------
        Nothing
        """
        if type == "horiz" or type == "vert":
            self._type = type
        else:
            assert 0, _("Bad type")

    def set_value(self, val=None):
        """ Define the location of the Cursor

        Parameter
        ---------
        val: float
        The position of the cursor. For 'horiz' type, this is the 'Y' coordinate
        and for 'vert' type, this is the 'X' coordinate

        Returns
        -------
        Nothing
        """
        if val is not None:
            self._value = val

    def set_visible(self, vis=None):
        """ Toggle status if called without argument
        otherwise set to the value

        Parameter
        ---------
        vis: bool or None
        True if the cursor shall be displayed on the Graph
        None to toggle the status
        """ 
        if isinstance(vis, bool):
            # Set
            self._visible = vis
        else:
            # Toggle
            if self._visible:
                self._visible = False
            else:
                self._visible = True

    value = property(get_value, set_value)
    type = property(get_type, set_type)
    visible = property(get_visible, set_visible)

    def get_line(self):
        """ Returns whether the Cursor is displayed or not

        Parameter
        ---------
        None

        Returns
        -------
        matplotlib.lines.Line2D
        The object used to represent the Cursor on the Graph
        """
        return self._line

    def __str__(self):
        """ Representation string of the Cursor

        Parameter
        ---------
        None

        Returns
        -------
        string:
        The representation of the Cursor
        'val: XXXX type: YYYYY vis: ZZZZZ'
        """
        return "val:" + str(self._value) + " type:" + self._type \
            + " vis:" + str(self._visible)
