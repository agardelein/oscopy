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

class Cursor:
    """ Handle cursors
    Cursor can be visible or not, type "horiz" or "vert"
    """
    def __init__(self, val, type):
        """ Set values
        """
        self.set_value(val)
        self.set_visible(True)
        self.line = None # Line2D
        self.set_type(type)

    def draw(self, ax = None, num = 0):
        """ Draw cursor on axis ax, num is the linestyle 0 for solid,
        non-zero for dashed
        """
        # Check whether cursor is within the axis limits
        if self.type == "horiz":
            lim = ax.get_ylim()
        elif self.type == "vert":
            lim = ax.get_xlim()
        else:
            return
        if self.val < lim[0] or self.val > lim[1]:
            # Outside axe limits, delete line and that's it
            self.line = None
            return

        # Cursor is within the limit
        if self.line == None or not self.line.get_axes() == ax:
            # Cursor do not exist on the graph, plot it
            ax.hold(True)
            if self.type == "horiz":
                x = ax.get_xlim()
                y = [self.val, self.val]
            elif self.type == "vert":
                x = [self.val, self.val]
                y = ax.get_ylim()
            else:
                return
            if num == 0:
                lt = ""
            else:
                lt = "--"
            self.line, = ax.plot(x, y, lt + "k")
            self.line.set_visible(self.vis)
            ax.hold(False)
        elif ax == self.line.get_axes():
            # Cursor already exist, just update visibility
            if self.type == "horiz":
                x = ax.get_xlim()
                y = [self.val, self.val]
            elif self.type == "vert":
                x = [self.val, self.val]
                y = ax.get_ylim()
            self.line.set_data(x, y)
            self.line.set_visible(self.vis)
        else:
            # Cursor exist already in this graph, nothing to do
            pass

    def get_type(self):
        return self.type

    def get_value(self):
        return self.val

    def get_visible(self):
        return self.vis

    def set_type(self, type = ""):
        if not type == "":
            if type == "horiz" or type == "vert":
                self.type = type

    def set_value(self, val = None):
        if not val == None:
            self.val = val

    def set_visible(self, vis = None):
        """ Toggle status if called without argument
        otherwise set_ to the value
        """ 
        if not vis == None:
            self.vis = vis
        else:
            if self.vis == True:
                self.vis = False
            else:
                self.vis = True

    def __str__(self):
        return "val:" + str(self.val) + " type:" + self.type \
            + " vis:" + str(self.vis)
