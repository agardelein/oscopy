""" Points list of a signal

A signal is the common point between the reader and the graph objects,
i.e. the file and the plot.

A signal contains a list of points, with an identifier, a reference (abscisse) and the original reader object.

The identifier is the signal name, as presented to the user.
The signal contains the ordinate values, while the abscisses are contained
into the reference signal.
The reference signal has its ref set_ to None.

The reader object is stored into the signal, if any use.

Class Signal -- Contains the signal points and other information
   __init(name, reader)__
      Create an empty signal.
      If given, set_ the name and the reader.

   set_[data|ref]()
      Set the data points of the signal and the reference signal respectively

   get_[data|ref|name|unit]()
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
import numpy

# Signals class
class Signal(object):
    def __init__(self, name="", unit=""):
        if isinstance(name, Signal):
            self._data = name._data
            self._name = name._name
            if name.ref is None:
                self._ref = name._ref
            else:
                self._ref = Signal(name._ref)
            self._unit = name._unit
            self._freeze = name.frozen
        else:
            self._data = []            # Data points
            self._name = name         # Identifier
            self._ref = None          # Reference signal
            self._unit = unit         # Unit of the signal
            self._freeze = False      # Flag for update

    def set_data(self, data=[]):
        """ Set the data points of the signal
        """
        if data is None:
            self._data = data
        elif len(data) > 0 :
            if isinstance(data, list):
                self._data = numpy.array(data)
            elif isinstance(data, numpy.ndarray):
                self._data = data
            else:
                assert 0, _("Data %s not handled") % type(data)

    def get_data(self):
        """ Return the list of point of the signal
        """
        return self._data

    def set_ref(self, ref=None):
        """ Set the reference signal
        If set_ to None, then signal is a reference signal (Time, Freq)
        """
        if ref is None or isinstance(ref, Signal):
            self._ref = ref
        else:
            return

    def get_ref(self):
        """ Return the reference signal
        """
        return self._ref

    @property
    def name(self):
        """ Return the signal name
        """
        return self._name

    @property
    def unit(self):
        """ Return the unit of the signal
        """
        return self._unit

    def get_freeze(self):
        """ Tell to update or not the signal
        """
        return self._freeze

    def set_freeze(self, frz=None):
        """ Tell to update or not the signal
        """
        if isinstance(frz, bool):
            self._freeze = frz
        else:
            assert 0, _("Bad type")

    def __str__(self):
        ref_name = self.ref.name if self.ref else '(no reference)'
        return '%s / %s %s' % (self.name, ref_name, self.unit)

    def __repr__(self):
        ref_name = self.ref.name if self.ref else '(no reference)'
        return '<%s[0x%x] %s / %s [%s]>' % (type(self).__name__, id(self),
                                            self.name, ref_name, self.unit)

    ref = property(get_ref, set_ref)
    data = property(get_data, set_data)
    freeze = property(get_freeze, set_freeze)
