""" Signal list,

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

   __str__()
      Returns a string with the signal name, the reference name
      and the reader name.
"""

# Signals class
class Signal:
    def __init__(self, name = "", reader = None):
        self.pts = []            # Data points
        self.name = name         # Identifier
        self.ref = None          # Reference signal
        self.reader = reader     # Reader object

    def __str__(self):
        a = self.name + " / " + (self.ref.name) + " (" + str(self.reader) + ") "
        b = ""
        if len(self.pts) > 10:
            for i in range(0, 9):
                b = b + self.pts[i] + "|"
        return a
