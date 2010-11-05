""" Interface between signals and figures

Class Context: Commands callables from oscopy commandline

   Methods:
   __init__()
   Create empty lists of figures, readers and signals

   create(sns)
   Create a new figure, and assign signals if provided

   destroy(num)
   Delete a figure

   figures()
   List of figures

   read(fn)
   Read signals from file fn

   write(fn, fmt, sns, opts)
   Write signals sns to file fn using format sns and options opts

   update()
   Reread all signals from files

   freeze(sns)
   Set the freeze flag of signals

   unfreeze(sns)
   Unset_ the freeze flag of signals

   signals()
   List all the signals

   math(expr)
   Create a signal from a mathematical expression

   names_to_signals(sns)
   Return a list of the signal names from the arguments provided by the user
   Should not be called from the command line

Abbreviations:
sigs: dict of sigs
sns : signal names
opts: options
fn  : filename
"""

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
        self._readers = {}
        self._figures = []
        self._signals = {}
        self._update_num = -1
        self._signal_name_to_reader = {}
        
    def create(self, sigs):
        """ Create a new figure and set it as current
        Can be either called from commandline or a function.
        When called from commandline, call names_to_signals to retrieve
        the signal list
        When called from a function, if the argument is not a list
        then return.
        After those tests, the figure is created with the signal list.
        """
        if isinstance(sigs, list):
            # Called from commandline,
            # Get the signal list from args
            if not sigs == "":
                sigs = self.names_to_signals(sigs)
            else:
                # No signal list provided
                sigs = {}
        elif not isinstance(sigs, dict):
            return
        # toplot is now a list
        f = Figure(sigs)
        self._figures.append(f)

    def destroy(self, num):
        """ Delete a figure
        User must provide the figure number.
        If the number is out of range, then return
        To avoid mixing numbers, just replace the figure by None in the list
        """
        if num > len(self._figures) or num < 1:
            assert 0, _("Out of range figure number")
        self._figures[num - 1] = None

    def read(self, fn):
        """ Read signals from file.
        Duplicate signal names overwrite the previous one.
        For new only gnucap files are supported.
        Do not load the same file twice.
        """
        # File already loaded ?
        if fn in self._readers.keys():
            raise _("File already loaded, use update to read it again")

        r = DetectReader(fn)
        if r is None:
            raise NotImplementedError()
        sigs = r.read(fn)

        # Insert signals into the dict
        for sn in sigs.keys():
            self._signals[sn] = sigs[sn]
            self._signal_name_to_reader[sn] = r
        self._readers[fn] = r
        return sigs

    def write(self, fn, fmt, sns, opts):
        """ Write signals to file
        """
        # Create the object
        sigs = self.names_to_signals(sns)
        if not sigs:
            return
        w = DetectWriter(fmt, fn, True)
        if w is not None:
            w.write(fn, sigs, opts)
        else:
            raise NotImplementedError()

    def update(self, r=None, upn=-1):
        """ Reread signal from files.
        For each file, reread it, and for updated, new and deleted signal,
        update the signal dict accordingly.
        Act recursively.
        """        ## SUPPORT FOR UPDATE SINGLE READER
        n = {}    # New signals
        if upn == -1:
            # Normal call create the new list etc etc
            self._update_num += 1
            if r is None:
                for reader in self._readers.itervalues():
                    #                print "Updating signals from", reader
                    n.update(self.update(reader, self._update_num))
            else:
                n.update(self.update(r, self._update_num))
        else:
            # First look at its dependencies
            if hasattr(r, "get_depends") and callable(r.get_depends):
                for sn in r.get_depends():
#                    print " Updating signals from", self._signal_name_to_reader[sn]
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
        # Delete signals from all graphs of all figures
        for f in self._figures:
            for g in f.graphs:
                g.remove(self.names_to_signals(d))
                g.update_signals()
            if f.canvas is not None:
                f.canvas.draw()
        for sn in d:
            del self._signals[sn]

    def freeze(self, sns):
        """ Set the freeze flag of signals
        """
        sigs = self.names_to_signals(sns)
        for s in sigs.itervalues():
            s.freeze = True

    def unfreeze(self, sns):
        """ Unset the freeze flag of signals
        """
        sigs = self.names_to_signals(sns)
        for s in sigs.itervalues():
            s.freeze = False

    @property
    def signals(self):
        """ List loaded signals
        """
        return self._signals

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
                            raise ReadError(_("What is %s") % sn)
                    r.set_origsigs(sigs)
                    ss = r.read(inp)

        for sn, s in ss.iteritems():
            self._signals[sn] = s
            self._signal_name_to_reader[sn] = r
        self._readers[inp] = r
        return ss

    def import_signal(self, sig, name):
        """ Import a signal from outside oscopy context
        """
        r = DetectReader(sig)
        ss = r.read((sig, name))
        for sn, s in ss.iteritems():
            self._signals[sn] = s
            self._signal_name_to_reader[sn] = r
        rname = "%s=%s" % (name, sig.name)
        self.readers[rname] = r
        return ss

    def names_to_signals(self, sns):
        """ Return a signal dict from the signal names list provided
        If no signals are found, return {}
        """
        if not sns or not self._signals:
            return {}
        sigs = {}

        # Prepare the signal list
        for sn in sns:
            if sn in self._signals.keys():
                sigs[sn] = self._signals[sn]
            else:
#                print sn + ": Not here"
                pass

        # No signals found
#        if not sigs:
#            print "No signals found"
        return sigs

    @property
    def figures(self):
        """ Return the figure list"""
        return self._figures

    @property
    def readers(self):
        """ Return the reader list"""
        return self._readers
