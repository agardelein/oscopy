""" Points list of a signal

A signal is the common point between the reader and the graph objects,
i.e. the file and the plot.

A signal contains a list of points, with an identifier, a reference (abscisse) and the original reader object.

The identifier is the signal name, as presented to the user.
The signal contains the ordinate values, while the abscisses are contained
into the reference signal.
The reference signal has its ref set to None.

The reader object is stored into the signal, if any use.

Class Signal -- Contains the signal points and other information
   __init(name, reader)__
      Create an empty signal.
      If given, set the name and the reader.

   set[pts|ref]()
      Set the data points of the signal and the reference signal respectively

   get[pts|ref|name|unit]()
      Return the signal data points, reference signal signal name
      and unit respectively

   update()
      Update the signal from the reader

   freeze(True|False|None)
      Toggle updating, if None return current status

   __str__()
      Returns a string with the signal name, the reference name
      and the reader name.
"""

# Signals class
class Signal:
    def __init__(self, name = "", reader = None, unit = ""):
        if isinstance(name, Signal):
            self.pts = name.pts
            self.name = name.name
            if name.ref == None:
                self.ref = name.ref
            else:
                self.ref = Signal(name.ref)
            self.reader = name.reader
            self.unit = name.unit
            self.frozen = name.frozen
        else:
            self.pts = []            # Data points
            self.name = name         # Identifier
            self.ref = None          # Reference signal
            self.reader = reader     # Reader object
            self.unit = unit         # Unit of the signal
            self.frozen = False      # Flag for update

    def setpts(self, pts = []):
        """ Set the data points of the signal
        """
        if pts == None:
            self.pts = pts
        elif len(pts) > 0 :
                self.pts = pts

    def getpts(self):
        """ Return the list of point of the signal
        """
        return self.pts

    def setref(self, ref = None):
        """ Set the reference signal
        If set to None, then signal is a reference signal (Time, Freq)
        """
        if ref == None or isinstance(ref, Signal):
            self.ref = ref
        else:
            return

    def getref(self):
        """ Return the reference signal
        """
        return self.ref

    def getname(self):
        """ Return the signal name
        """
        return self.name

    def getunit(self):
        """ Return the unit of the signal
        """
        return self.unit

    def gerreader(self):
        """ Return the reader
        """
        return self.reader

    def update(self, upn, keep = True):
        """ Update the signal trough the reader
        Do not update if frozen is set.
        If keep is false, erase points.
        Return a list of new signals
        """
        if self.frozen == True:
            return {}
        # Update from the reader
        return self.reader.update(self, upn, keep)

    def freeze(self, frz = None):
        """ Tell to update or not the signal
        """
        if not frz == None:
            if frz == True or frz == False:
                self.frozen = frz
        return self.frozen

    def __str__(self):
        a = self.name + " / " + (self.ref.name) \
            + " " + self.unit \
            + " (" + str(self.reader) + ") "
        b = ""
        if len(self.pts) > 10:
            for i in range(0, 9):
                b = b + str(self.pts[i]) + "|"
        return a
