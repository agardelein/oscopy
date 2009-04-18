""" Common file read functions

Class ReadError -- Errors encountered when loading file
   methods:
   __init__(value)
      Assign the error message

   __str__()
      Return a string with the error message

Class Reader -- Define the common functions for reader objects

   methods:
   read(fi)
      Check if the file can be opened before calling read_sigs(),

   read_sigs()
      To be defined into the derived objects
      Read the signals from the file, fill slist
      and return a dict of the signals, with the signame as key.

   update()
      Reread the file and return a dict of the reread signals,
      toget_her with a list of the updated, deleted and added signals

   detect(fn)
      Return  if the object recognize the file

   check(fn)
      Raise ReadError exception if file fn is not accessible

   __str__()
      Return the filename

"""

import os.path

class ReadError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class Reader(object):
    """ Reader -- Provide common function for signal file reading
    The derived class must redefine read_sigs() and detect()
    """
    def __init__(self):
        self.fn = ""
        self.sigs = {}
        self.upn = -1  # Update number

    # Certify the path is valid and is a file
    def read(self, fn):
        """ Check if the path is a valid file and call read_sigs
        """
        self.check(fn)
        self.fn = fn
        return self.read_sigs()

    def read_sigs(self):
        """ Read the signal list from the file, fill self.slist
        and return a dict of the signals, with the signal name as a key
        """
        return {}

    # Re-read the data file
    # Return signal list and names of updated, deleted and new signals
    def update(self, upn, keep=True):
        """ On new update requests (upn > self.upn), reread the file
        and update self.sigs.
        Update signals, but if unit or reference is not found,
        mark signal as being deleted if keep is False (see below)
        If read_sigs returns nothing (file is deleted or whatever), all
        signals are considered deleted
        If signal is not found or either reference or unit changed, de
        If keep is False, the signal is marked as being deleted, i.e. its
        data set to None
        Return dict of new signals
        """
        if upn <= self.upn:
            # Already updated
            return {}

        # Save the old list and reread the file
        oldsigs = self.sigs
        sigs = self.read_sigs()
        # Update the old signal dict with new one
        # Find the new signals, update signals not frozen, mark deleted signals
        # and for updated signals check whether ref, ref unit or unit
        # has changed
        n = {}
        for sn, s in sigs.iteritems():
            if sn not in oldsigs:
                # New signal
                n[sn] = s
                oldsigs[sn] = s
 #               print "New signal:", sn
            else:
                if oldsigs[sn].freeze():
                    # Signal is frozen, no update
 #                   print sn, "is frozen"
                    continue
                os = oldsigs[sn]
                ns = sigs[sn]
                if os.get_unit() == ns.get_unit() and \
                        os.get_ref().get_unit() == ns.get_ref().get_unit() and \
                        os.get_ref().get_name() == ns.get_ref().get_name():
                    # Unit, reference unit and reference name are the same so
                    # Update !
                    os.get_ref().set_data(ns.get_ref().get_data())
                    os.set_data(ns.get_data())
 #                   print os.get_name(), "updated !"
                else:
                    # Something changed, do not update
                    if not keep:
                        os.set_data(None)
 #                   print os.get_name(), "not updated: something changed"

        # Find deleted signals, i.e. present in old dict but not in new one
        for sn, s in oldsigs.iteritems():
            if sn not in sigs:
                if not keep:
                    s.set_data(None)
 #                   print s.get_name(), "DELETED !"
        self.upn = upn
        self.sigs = oldsigs
        return n

    def detect(self, fn):
        """ Check if the file provided can be read by this object
        """
        return False

    def check(self, fn):
        """ Check if the file is accessible
        Raise ReadError exception if not accessible
        """
        if not fn:
            raise ReadError("No file specified")
        if not os.path.exists(fn):
            raise ReadError("File do not exist")
        if not os.path.isfile(fn):
            raise ReadError("File is not a file")

    def __str__(self):
        """ Return the signal name.
        """
        return self.fn
