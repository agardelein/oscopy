""" Interface between signals and figures

Class Oscopy: Commands callables from oscopy commandline

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

   signames_to_sigs(sns)
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
from Readers.DetectReader import DetectReader
from Writers.DetectWriter import DetectWriter
from Readers.Reader import ReadError
from Writers.Writer import WriteError
from figure import Figure

class Oscopy(object):
    """ Class Oscopy -- Interface between signals and figures

    This object is the interface between the signals and the figures,
    e.g. it handle operations on figures, signals, readers and writers.
    It maintain a list of figures, a dict of reader and a dict of signals.
    
    The keys for the signal dict are the signal name, as presented to the user
    The keys for the reader dict are the file name.
    """

    def __init__(self):
        """ Create the instance variables
        """
        self.curfig = None
        self.readers = {}
        self.figs = []
        self.sigs = {}
        self.upn = -1
        self.sn_to_r = {}
        
    def create(self, sigs):
        """ Create a new figure and set_ it as current
        Can be either called from commandline or a function.
        When called from commandline, call signames_to_sigs to retrieve
        the signal list
        When called from a function, if the argument is not a list
        then return.
        After those tests, the figure is created with the signal list.
        """
        if isinstance(sigs, list):
            # Called from commandline,
            # Get the signal list from args
            if not sigs == "":
                sigs = self.signames_to_sigs(sigs)
            else:
                # No signal list provided
                sigs = {}
        elif not isinstance(sigs, dict):
            return
        # toplot is now a list
        f = Figure(sigs)
        self.figs.append(f)
        self.curfig = f

    def destroy(self, num):
        """ Delete a figure
        User must provide the figure number.
        If the number is out of range, then return
        Act as a "pop" with self.curfig
        """
        if num > len(self.figs) or num < 1:
            return
        if self.curfig == self.figs[num - 1]:
            if len(self.figs) == 1:
                # Only one element remaining in the list
                self.curfig = None
            elif num == len(self.figs):
                # Last element, go to the previous
                self.curfig = self.figs[num - 2]
            else:
                # Go to next element
                self.curfig = self.figs[num]
        del self.figs[num - 1]
        if self.curfig is not None:
            print "Curfig : ", self.figs.index(self.curfig) + 1
        else:
            print "No figures"

    def select(self, num, gn = 0):
        """ Select the current figure
        """
        if num > len(self.figs) or num < 1:
            return
        self.curfig = self.figs[num - 1]
        if gn > 0:
            self.curfig.select(gn)

    def layout(self, l):
        """ Define the layout of the current figure
        """
        if self.curfig is not None:
            self.curfig.set_layout(l)

    def figlist(self):
        """ Print the list of figures
        """
        for i, f in enumerate(self.figs):
            if f == self.curfig:
                print "*",
            else:
                print " ",
            print "Figure", i + 1, ":", f.layout
            f.list()

    def plot(self):
        """ Plot the figures, and enter in the matplotlib main loop
        """
        if not self.figs:
            return
        for i, f in enumerate(self.figs):
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
        if fn in self.readers.keys():
            print "File already loaded"
            return

        r = DetectReader(fn)
        if r is None:
            print "File format unknown"
            return
        sigs = r.read(fn)

        # Insert signals into the dict
        for sn in sigs.keys():
            self.sigs[sn] = sigs[sn]
            self.sn_to_r[sn] = r
        print fn, ":"
        for s in sigs.itervalues():
            print s
        self.readers[fn] = r

    def write(self, fn, fmt, sns, opts):
        """ Write signals to file
        """
        # Create the object
        sigs = self.signames_to_sigs(sns)
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
            self.upn += 1
            for reader in self.readers.itervalues():
                print "Updating signals from", reader
                n.update(self.update(reader, self.upn))
        else:
            # First look at its dependencies
            if hasattr(r, "get_depends") and callable(r.get_depends):
                for sn in r.get_depends():
                    print " Updating signals from", self.sn_to_r[sn]
                    n.update(self.update(self.sn_to_r[sn], self.upn))
                    # TODO: Update depencies: what happens to vo when
                    # vout is deleted ? It seems it is not deleted: it should!
            # Update the reader
            n.update(r.update(self.upn, keep=False))
            return n

        # Find deleted signals
        d = []
        for sn, s in self.sigs.iteritems():
            #n.update(s.update(self.upn, False))
            if s.data is None:
                d.append(sn)
        # Insert new signals
        self.sigs.update(n)
        # Delete signals: first from figure and after from dict
        for sn in d:
            for f in self.figs:
                f.remove({sn:self.sigs[sn]}, "all")
            del self.sigs[sn]

    def add(self, sns):
        """ Add a graph to the current figure
        The signal list is a coma separated list of signal names
        If no figure exist, create a new one.
        """
        if not self.figs:
            self.create(sns)
        else:
            sigs = self.signames_to_sigs(sns)
            self.curfig.add(sigs)

    def delete(self, gn):
        """ Delete a graph from the current figure
        """
        if self.curfig is not None:
            self.curfig.delete(gn)

    def mode(self, mode):
        """ Set the mode of the current graph of the current figure
        """
        if self.curfig is not None:
            self.curfig.set_mode(mode)

    def scale(self, sc):
        """ Set the axis scale of the current graph of the current figure
        """
        if self.curfig is not None:
            self.curfig.set_scale(sc)

    def range(self, a1 = "reset", a2 = None, a3 = None, a4 = None):
        """ Set the axis range of the current graph of the current figure
        """
        if self.curfig is not None:
            self.curfig.set_range(a1, a2, a3, a4)

    def unit(self, xu, yu = ""):
        """ Set the units of current graph of current figure
        """
        if self.curfig is not None:
            self.curfig.set_unit(xu, yu)        
            
    def insert(self, sns):
        """ Insert a list of signals into the current graph 
        of the current figure
        """
        if not self.figs:
            return

        if self.curfig is not None:
            sigs = self.signames_to_sigs(sns)
            self.curfig.insert(sigs)

    def remove(self, sns):
        """ Remove a list of signals from the current graph
        of the current figure
        """
        if not self.figs:
            return

        if self.curfig is not None:
            sigs = self.signames_to_sigs(sns)
            self.curfig.remove(sigs)

    def freeze(self, sns):
        """ Set the freeze flag of signals
        """
        sigs = self.signames_to_sigs(sns)
        for s in sigs.itervalues():
            s.freeze = True

    def unfreeze(self, sns):
        """ Unset the freeze flag of signals
        """
        sigs = self.signames_to_sigs(sns)
        for s in sigs.itervalues():
            s.freeze = False

    def siglist(self):
        """ List loaded signals
        """
        for s in self.sigs.itervalues():
            print s

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
                        if self.sigs.has_key(sn):
                            sigs[sn] = self.sigs[sn]
                        else:
                            print "What is", sn
                    r.set_origsigs(sigs)
                    ss = r.read(inp)
                    if not ss:
                        print "Signal not generated"
        for sn, s in ss.iteritems():
            self.sigs[sn] = s
            self.sn_to_r[sn] = inp
        self.readers[inp] = r

    def signames_to_sigs(self, sns):
        """ Return a signal dict from the signal names list provided
        If no signals are found, return {}
        """
        if not sns:
            return {}
        sigs = {}
        # Are there signals ?
        if not self.sigs:
            print "No signal loaded"
            return {}

        # Prepare the signal list
        for sn in sns:
            if sn in self.sigs.keys():
                sigs[sn] = self.sigs[sn]
            else:
                print sn + ": Not here"

        # No signals found
        if not sigs:
            print "No signals found"
            return {}
        return sigs

