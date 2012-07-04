from readers.detect_reader import DetectReader
from readers.reader import ReadError
from writers.detect_writer import DetectWriter
from writers.writer import WriteError
from figure import Figure
import gobject

class Context(gobject.GObject):
    """ Class Context -- Interface between signals, files and figures

This object is the interface between the signals, the files and the figures.
It gathers operations on figures, signals, readers and writers and thus
can be used for a program such ioscopy.
It maintain a list of figures, a dict of reader and a dict of signals.
    
Signals are stored in a dict according to their user name (Signal.name)
Files are stored in a dict according to their name

Properties
   signals  read/write   Dict of Signals read
   readers  read/write   Dict of Readers used
   figures  read/write   Dict of Figures instanciated

Signals
   'begin-transaction' is received to notify that Dependancy Signal data is
   being changed. Event re-emitted toward Listeners
   'end-transaction' is emitted once the Result Signal data is recomputed
   to notify Listeners that they can recompute their own data

Abbreviations
   sigs: dict of sigs
   sns : signal names
   opts: options
   fn  : filename
   """
    __gsignals__ = {
        'begin-transaction': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'end-transaction': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }

    def __init__(self):
        """ Create the instance variables

        Parameters
        ----------
        None

        Returns
        -------
        Object instanciated
        """
        gobject.GObject.__init__(self)
        self._readers = {}
        self._figures = []
        self._signals = {}
        self._update_num = -1
        self._signal_name_to_reader = {}
        
    def create(self, args):
        """ Instanciate a new figure
        No error reported if parameter type mismatches, silently does nothing

        Parameters
        ----------
        args: string or list of signals or Figure or dict of Signals
        Contains the list of signals for the Figure instanciation
        See also Figure.Figure()

        Returns
        -------
        Nothing
        """
        f = None
        if isinstance(args, list):
            # Called from commandline,
            # Get the signal list from args
            if not args == "":
                sigs = self.names_to_signals(args)
            else:
                # No signal list provided
                sigs = {}
            f = Figure(sigs)
        elif isinstance(args, Figure):
            # Already initialized figure provided
            f = args
        elif isinstance(args, dict):
            # Dict of Signals provided
            sigs = args
            f = Figure(sigs)
        if f is not None:
            self._figures.append(f)

    def destroy(self, num):
        """ Delete a figure
        If num is out of range issue an assertion.
        Figure is replaced by None in the list to keep code simple
        
        Parameters
        ----------
        num: integer
        The number of the figure to destroy

        Returns
        -------
        Nothing
        """
        if num > len(self._figures) or num < 1:
            assert 0, _("Out of range figure number")
        self._figures[num - 1] = None

    def read(self, fn):
        """ Read signals from file
        Overwrite signals in case of Signal name conflict.
        On success, Reader and Signals are added in the lists.

        Parameters
        ----------
        fn: string
        The file name

        Returns
        -------
        sigs: Dict of Signals
        List of Signals read from the file

        Raises
        ------
        string
        Do not read the same file twice

        NotImplementedError
        When the file type is not managed by any Reader
        """
        # File already loaded ?
        if fn in self._readers.keys():
            raise _("File already loaded, use update to read it again")

        r = DetectReader(fn)
        if r is None:
            raise NotImplementedError()
        sigs = r.read(fn)
        self.connect('begin-transaction', r.on_begin_transaction)
        self.connect('end-transaction', r.on_end_transaction)

        # Insert signals into the dict
        for sn in sigs.keys():
            self._signals[sn] = sigs[sn]
            self._signal_name_to_reader[sn] = r
        self._readers[fn] = r
        return sigs

    def write(self, fn, fmt, sns, opts):
        """ Write signals to file

        Parameters
        ----------
        fn: string
        The file name

        fmt: string
        The file format

        sns: dict of Signals
        The Signals to record

        opts: string
        List of options to pass to the Writer

        Returns
        -------
        Nothing

        Raises
        ------
        NotImplementedError
        When the file type is not managed by any Writer
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
        update the Signal dict accordingly.
        Act recursively.

        Note: recursion is now deprecated by using GObject event system by
        Signals, it will be removed in a future release

        Parameters
        ----------
        r: Reader
        Update Signals from this Reader only

        upn: integer
        Reserved for internal use (recursion) should always be the default value

        Returns
        -------
        n: new Signals
        """        ## SUPPORT FOR UPDATE SINGLE READER
        n = {}    # New signals
        if upn == -1:
            self.emit('begin-transaction')
            # Normal call create the new list etc etc
            self._update_num += 1
            if r is None:
                for reader in self._readers.itervalues():
                    #                print "Updating signals from", reader
                    n.update(self.update(reader, self._update_num))
            else:
                n.update(self.update(r, self._update_num))
            self.emit('end-transaction')
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
        """ Set the freeze flag of signals, i.e. disable updates

        Parameters
        ----------
        sns: dict of Signals
        Signals list to be frozen

        Returns
        -------
        Nothing
        """
        sigs = self.names_to_signals(sns)
        for s in sigs.itervalues():
            s.freeze = True

    def unfreeze(self, sns):
        """ Unset the freeze flag of signals, i.e. enable updates

        Parameters
        ----------
        sns: dict of Signals
        Signals list to be unfrozen

        Returns
        -------
        Nothing
        """
        sigs = self.names_to_signals(sns)
        for s in sigs.itervalues():
            s.freeze = False

    @property
    def signals(self):
        """ Dict of loaded signals

        Parameters
        ----------
        Nothing

        Returns
        -------
        dict of Signals
        List of Signals currently loaded in this Context
        """
        return self._signals

    def import_signal(self, sig, name):
        """ Import a signal from outside this Context

        Parameters
        ----------
        sig: Signal
        Signal to be imported

        name: string
        Name to be assigned to the Signal in this Context

        Returns
        -------
        ss: dict of Signals
        Contains only one element, the Signal imported

        Example
        -------
        >>> ctxt=oscopy.Context()
        >>> ctxt.read('demo/tran.dat')
        >>> ctxt.signals
        >>> v1=oscopy.Signal('v1', 'V')
        >>> ctxt.import_signal(v1, 'v1imported')
        >>> ctxt.signals
        """
        r = DetectReader(sig)
        ss = r.read((sig, name))
        for sn, s in ss.iteritems():
            self._signals[sn] = s
            self._signal_name_to_reader[sn] = r
            # FIXME: Probleme, comment gerer les dependances ?
            
        rname = "%s=%s" % (name, sig.name)
        self.readers[rname] = r
        return ss

    def names_to_signals(self, sns):
        """ Return a signal dict from the signal names list provided
        If no signals are found, return {}
        Use this function is reserved, will be made private in a future release

        Parameters
        ----------
        sns: list of string
        The list of name of Signals to retrieve

        Returns
        -------
        sigs: dict of Signals
        The list of Signals found in this Context
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
        """ Return the figure list

        Parameters
        ----------
        Nothing

        Returns
        -------
        List of Figures managed in this Context
        """
        return self._figures

    @property
    def readers(self):
        """ Return the reader list

        Parameters
        ----------
        Nothing

        Returns
        -------
        List of Readers managed in this Context
        """
        return self._readers
