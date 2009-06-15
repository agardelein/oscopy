""" Interface between signals and figures

Class Context: Commands callables from oscopy commandline

   Methods:
   __init__()
   Create empty lists of figures, readers and signals

   create(sns)
   Create a new figure, and assign signals if provided

   destroy(num)
   Delete a figure

   select(num, gn = 0)
   Select the figure and the graph to become the current ones

   layout(l)
   set_ the layout of the current figure

   figlist()
   Print a list of figures

   plot()
   plot all the figure

   read(fn)
   Read signals from file fn

   write(fn, fmt, sns, opts)
   Write signals sns to file fn using format sns and options opts

   update()
   Reread all signals from files

   add(sns)
   Add a graph to the current figure

   delete(gn)
   Delete a graph from the current figure

   mode(mode)
   Set the mode of the current graph

   scale(sc)
   Set the axis scale of the current graph e.g. log or lin

   range(a1, a2, a3, a4)
   Set the axis range of the current graph

   unit(xu, yu)
   Set the unit of current graph from current figure

   insert(sns)
   Add signals to the current graph of the current figure

   remove(sns)
   Remove signals from the current graph of the current figure

   freeze(sns)
   Set the freeze flag of signals

   unfreeze(sns)
   Unset_ the freeze flag of signals

   siglist()
   List all the signals

   math(expr)
   Create a signal from a mathematical expression

   _names_to_signals(sns)
   Return a list of the signal names from the arguments provided by the user
   Should not be called from the command line

Abbreviations:
sigs: dict of sigs
sns : signal names
opts: options
fn  : filename
gn  : graph number
"""

import sys
import re
import matplotlib.pyplot as plt
from readers.detect_reader import DetectReader
from readers.reader import ReadError
from writers.detect_writer import DetectWriter
from writers.writer import WriteError
from figure import Figure

class Context(object):
    """ Class Context -- Interface between signals and figures

    This object is the interface between the signals and the figures,
    e.g. it handle operations on figures, signals, readers and writers.
    It maintain a list of figures, a dict of reader and a dict of signals.
    
    The keys for the signal dict are the signal name, as presented to the user
    The keys for the reader dict are the file name.
    """

    def __init__(self):
        """ Create the instance variables
        """
        self._current = None
        self._readers = {}
        self._figures = []
        self._signals = {}
        self._update_num = -1
        self._signal_name_to_reader = {}
        
    def create(self, sigs):
        """ Create a new figure and set_ it as current
        Can be either called from commandline or a function.
        When called from commandline, call _names_to_signals to retrieve
        the signal list
        When called from a function, if the argument is not a list
        then return.
        After those tests, the figure is created with the signal list.
        """
        if isinstance(sigs, list):
            # Called from commandline,
            # Get the signal list from args
            if not sigs == "":
                sigs = self._names_to_signals(sigs)
            else:
                # No signal list provided
                sigs = {}
        elif not isinstance(sigs, dict):
            return
        # toplot is now a list
        f = Figure(sigs)
        self._figures.append(f)
        self._current = f

    def destroy(self, num):
        """ Delete a figure
        User must provide the figure number.
        If the number is out of range, then return
        Act as a "pop" with self._current
        """
        if num > len(self._figures) or num < 1:
            assert 0, "Out of range figure number"
        if self._current == self._figures[num - 1]:
            if len(self._figures) == 1:
                # Only one element remaining in the list
                self._current = None
            elif num == len(self._figures):
                # Last element, go to the previous
                self._current = self._figures[num - 2]
            else:
                # Go to next element
                self._current = self._figures[num]
        del self._figures[num - 1]
        if self._current is not None:
            print "Curfig : ", self._figures.index(self._current) + 1
        else:
            print "No figures"

    def get_current(self):
        """ Return the selected figure and graph
        """
        return self._figures.index(self._current) + 1, self._current.current

    def set_current(self, currents):
        """ Select the current figure
        """
        if not isinstance(currents, tuple) or len(currents) != 2:
            assert 0, "Bad type"
        num = currents[0]
        gn = currents[1]

        if num > len(self._figures) or num < 1:
            assert 0, "Out of range figure number"
        self._current = self._figures[num - 1]
        if gn > 0:
            self._current.current = gn

    def get_layout(self):
        """ Define the layout of the current figure
        """
        if self._current is not None:
            return self._current.layout
        else:
            assert 0, "No figure selected"

    def set_layout(self, layout):
        """ Define the layout of the current figure
        """
        if self._current is not None:
            self._current.layout = layout
        else:
            assert 0, "No figure selected"

    def figlist(self):
        """ Print the list of figures
        """
        for i, f in enumerate(self._figures):
            if f == self._current:
                print "*",
            else:
                print " ",
            print "Figure", i + 1, ":", f.layout
            f.list()

    def plot(self):
        """ Plot the figures, and enter in the matplotlib main loop
        """
        if not self._figures:
            assert 0, "No figure to plot"
        for i, f in enumerate(self._figures):
            fig = plt.figure(i + 1)
            f.plot(fig)
        plt.show()

    def read(self, fn):
        """ Read signals from file.
        Duplicate signal names overwrite the previous one.
        For new only gnucap files are supported.
        Do not load the same file twice.
        """
        # File already loaded ?
        if fn in self._readers.keys():
            print "File already loaded"
            return

        r = DetectReader(fn)
        if r is None:
            print "File format unknown"
            return
        sigs = r.read(fn)

        # Insert signals into the dict
        for sn in sigs.keys():
            self._signals[sn] = sigs[sn]
            self._signal_name_to_reader[sn] = r
        print fn, ":"
        for s in sigs.itervalues():
            print s
        self._readers[fn] = r

    def write(self, fn, fmt, sns, opts):
        """ Write signals to file
        """
        # Create the object
        sigs = self._names_to_signals(sns)
        if len(sigs) < 1:
            return
        try:
            w = DetectWriter(fmt, fn, True)
        except WriteError, e:
            print "Write error:", e
            return
        if w is not None:
            try:
                w.write(fn, sigs, opts)
            except WriteError, e:
                print "Write error:", e

    def update(self, r=None, upn=-1):
        """ Reread signal from files.
        For each file, reread it, and for updated, new and deleted signal,
        update the signal dict accordingly.
        """
        n = {}    # New signals
        if r is None:
            # Normal call create the new list etc etc
            self._update_num += 1
            for reader in self._readers.itervalues():
                print "Updating signals from", reader
                n.update(self.update(reader, self._update_num))
        else:
            # First look at its dependencies
            if hasattr(r, "get_depends") and callable(r.get_depends):
                for sn in r.get_depends():
                    print " Updating signals from", self._signal_name_to_reader[sn]
                    n.update(self.update(self._signal_name_to_reader[sn], self._update_num))
                    # TODO: Update depencies: what happens to vo when
                    # vout is deleted ? It seems it is not deleted: it should!
            # Update the reader
            n.update(r.update(self._update_num, keep=False))
            return n

        # Find deleted signals
        d = []
        for sn, s in self._signals.iteritems():
            #n.update(s.update(self._update_num, False))
            if s.data is None:
                d.append(sn)
        # Insert new signals
        self._signals.update(n)
        # Delete signals: first from figure and after from dict
        for sn in d:
            for f in self._figures:
                f.remove({sn:self._signals[sn]}, "all")
            del self._signals[sn]

    def add(self, sns):
        """ Add a graph to the current figure
        The signal list is a coma separated list of signal names
        If no figure exist, create a new one.
        """
        if not self._figures:
            self.create(sns)
        else:
            sigs = self._names_to_signals(sns)
            self._current.add(sigs)

    def delete(self, gn):
        """ Delete a graph from the current figure
        """
        if self._current is not None:
            self._current.delete(gn)
        else:
            assert 0, "No figure selected"

    def get_mode(self):
        """ Return the mode of the current graph of the current figure
        """
        if self._current is not None:
            return self._current.mode
        else:
            assert 0, "No figure selected"
        

    def set_mode(self, mode):
        """ Set the mode of the current graph of the current figure
        """
        if self._current is not None:
            self._current.mode = mode
        else:
            assert 0, "No figure selected"

    def get_scale(self):
        """ Return the axis scale of the current graph of the current figure
        """
        if self._current is not None:
            return self._current.scale
        else:
            assert 0, "No figure selected"

    def set_scale(self, scale):
        """ Set the axis scale of the current graph of the current figure
        """
        if self._current is not None:
            self._current.scale = scale
        else:
            assert 0, "No figure selected"

    def get_range(self):
        """ Return the axis range of the current graph of the current figure
        """
        if self._current is not None:
            return self._current.range
        else:
            assert 0, "No figure selected"

    def set_range(self, range):
        """ Set the axis range of the current graph of the current figure
        """
        if self._current is not None:
            self._current.range = range
        else:
            assert 0, "No figure selected"

    def get_unit(self):
        """ Return the units of current graph of current figure
        """
        if self._current is not None:
            return self._current.unit
        else:
            assert 0, "No figure selected"
            
    def set_unit(self, unit):
        """ Set the units of current graph of current figure
        """
        if self._current is not None:
            self._current.unit = unit
        else:
            assert 0, "No figure selected"
            
    def insert(self, sns):
        """ Insert a list of signals into the current graph 
        of the current figure
        """
        if not self._figures:
            assert 0, "No figure present"

        if self._current is not None:
            sigs = self._names_to_signals(sns)
            self._current.insert(sigs)
        else:
            assert 0, "No figure selected"

    def remove(self, sns):
        """ Remove a list of signals from the current graph
        of the current figure
        """
        if not self._figures:
            assert 0, "No figure present"

        if self._current is not None:
            sigs = self._names_to_signals(sns)
            self._current.remove(sigs)
        else:
            assert 0, "No figure selected"

    def freeze(self, sns):
        """ Set the freeze flag of signals
        """
        sigs = self._names_to_signals(sns)
        for s in sigs.itervalues():
            s.freeze = True

    def unfreeze(self, sns):
        """ Unset the freeze flag of signals
        """
        sigs = self._names_to_signals(sns)
        for s in sigs.itervalues():
            s.freeze = False

    def siglist(self):
        """ List loaded signals
        """
        signals = []
        for r_name, reader in self._readers.iteritems():
            signals = signals +\
                map(lambda x: {"name":x.name, "unit":x.unit,\
                                   "reference":x.ref.name,\
                                   "reader": r_name},\
                        reader.signals.values())

        return signals

    def math(self, inp):
        """ Create a signal from mathematical expression
        """
        sigs = {}

        # Create the expression
        r = DetectReader(inp)
        ss = r.read(inp)
        if not ss:
            # Failed to read file
            # If reader provide a missing() and set_origsigs() functions
            # and if signal names are found pass them to reader
            if hasattr(r, "missing") and callable(r.missing):
                sns = r.missing()
                if hasattr(r, "set_origsigs") and callable(r.set_origsigs):
                    for sn in sns:
                        if self._signals.has_key(sn):
                            sigs[sn] = self._signals[sn]
                        else:
                            print "What is", sn
                    r.set_origsigs(sigs)
                    ss = r.read(inp)
                    if not ss:
                        print "Signal not generated"
        for sn, s in ss.iteritems():
            self._signals[sn] = s
            self._signal_name_to_reader[sn] = inp
        self._readers[inp] = r

    def _names_to_signals(self, sns):
        """ Return a signal dict from the signal names list provided
        If no signals are found, return {}
        """
        if not sns:
            return {}
        sigs = {}
        # Are there signals ?
        if not self._signals:
            print "No signal loaded"
            return {}

        # Prepare the signal list
        for sn in sns:
            if sn in self._signals.keys():
                sigs[sn] = self._signals[sn]
            else:
                print sn + ": Not here"

        # No signals found
        if not sigs:
            print "No signals found"
            return {}
        return sigs

    layout = property(get_layout, set_layout)
    mode = property(get_mode, set_mode)
    scale = property(get_scale, set_scale)
    range = property(get_range, set_range)
    unit = property(get_unit, set_unit)
    current = property(get_current, set_current)
