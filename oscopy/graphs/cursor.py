""" Handle cursors in plots

A cursor is an horizontal or vertical line drawn across the plot,
depending on type, either "horiz" or "vert".
The line position depends on the value.
It can be visible or not.
It contains an alias to the Line2D object in the plot.

methods:
   __init__(val, type):
   Create the object

   draw(ax, num):
   Draw the cursor on the Axe ax with line style depending on num.
   If num is 0 then use solid line else use dashed style.

   [get_|set_]_[value|visible|type](...)
   Accessors to the object members

   __str()__
   Return a string containing the main values of the object
"""

class Cursor(object):
    """ Handle cursors
    Cursor can be visible or not, type "horiz" or "vert"
    """
    def __init__(self, val, type):
        """ Set values
        """
        self.set_value(val)
        self.set_visible(True)
        self._line = None # Line2D
        self.set_type(type)

    def draw(self, ax=None, num=0):
        """ Draw cursor on axis ax, num is the linestyle 0 for solid,
        non-zero for dashed
        """
        # Check whether cursor is within the axis limits
        if self._type == "horiz":
            lim = ax.get_ylim()
        elif self._type == "vert":
            lim = ax.get_xlim()
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
            if self._type == "horiz":
                x = ax.get_xlim()
                y = [self._value, self._value]
            elif self._type == "vert":
                x = [self._value, self._value]
                y = ax.get_ylim()
            else:
                return
            if num == 0:
                lt = ""
            else:
                lt = "--"
            self._line, = ax.plot(x, y, lt + "k")
            self._line.set_visible(self._visible)
            ax.hold(False)
        elif ax == self._line.get_axes():
            # Cursor already exist, just update visibility
            if self._type == "horiz":
                x = ax.get_xlim()
                y = [self._value, self._value]
            elif self._type == "vert":
                x = [self._value, self._value]
                y = ax.get_ylim()
            self._line.set_data(x, y)
            self._line.set_visible(self._visible)
        else:
            # Cursor exist already in this graph, nothing to do
            pass

    def get_type(self):
        return self._type

    def get_value(self):
        return self._value

    def get_visible(self):
        return self._visible

    def set_type(self, type=""):
        if type == "horiz" or type == "vert":
            self._type = type
        else:
            assert 0, "Bad type"

    def set_value(self, val=None):
        if val is not None:
            self._value = val

    def set_visible(self, vis=None):
        """ Toggle status if called without argument
        otherwise set_ to the value
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

    def __str__(self):
        return "val:" + str(self._value) + " type:" + self._type \
            + " vis:" + str(self._visible)
