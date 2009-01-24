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
      Check if the file can be opened before calling readsigs(),

   readsigs()
      To be defined into the derived objects
      Read the signals from the file, fill slist
      and return a dict of the signals, with the signame as key.

   update()
      Reread the file and return a dict of the reread signals,
      together with a list of the updated, deleted and added signals

   detect(fn)
      Return  if the object recognize the file

   __str__()
      Return the filename

"""

import os.path

class ReadError:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "File error :", value

class Reader:
    """ Reader -- Provide common function for signal file reading
    The derived class must redefine readsigs()
    """
    def __init__(self):
        self.fn = ""
        self.sigs = {}
        self.upn = -1  # Update number

    # Certify the path is valid and is a file
    def read(self, fi):
        """ Check if the path is a valid file and call readsigs
        """
        if fi == "":
            raise ReadError("No file specified")
        if not os.path.exists(fi):
            raise ReadError("File do not exist")
        if not os.path.isfile(fi):
            raise ReadError("File is not a file")
        self.fn = fi
        return self.readsigs()

    def readsigs(self):
        """ Read the signal list from the file, fill self.slist
        and return a dict of the signals, with the signal name as a key
        """
        return {}

    # Re-read the data file
    # Return signal list and names of updated, deleted and new signals
    def update(self, sig, upn, keep = True):
        """ On new update requests (upn > self.upn), reread the file
        and update self.slist.
        Update sig, but if unit or reference is not found set pts to
        None 
        If readsigs returns nothing (file is deleted or whatever), all
        signals are considered deleted
        If signal is not found or either reference or unit changed, de
        Return dict of new signals
        """
        n = {}
        if upn > self.upn:
            oldl = self.slist
            sigs = self.readsigs()
            # Find new signals
            for sn, s in sigs.iteritems():
                found = 0
                for os in oldl:
                    if os.name == sn:
                        found = 1
                        break
                if not found:
                    n[sn] = s
            self.upn = upn
        else:
            sigs = {}
            for s in self.slist:
                sigs[s.name] = s
        sn = sig.name
        if sigs.has_key(sn):
            # Check unit, reference unit, reference name
            if sigs[sn].getunit() == sig.getunit() \
                    and sigs[sn].getref().getunit() == sig.getref().getunit() \
                    and sigs[sn].getref().getname() == sig.getref().getname():
                sig.getref().setpts(sigs[sn].getref().getpts())
                sig.setpts(sigs[sn].getpts())
            else:
                print "Signal", sn, "not updated: reference or unit has changed"
                if not keep:
                    sig.setpts(None)
                return n
        else:
            print "Signal", sn, "not updated: signal name not found"
            if not keep:
                sig.setpts(None)
            return {}
        return n

    def detect(self, fn):
        """ Check if the file provided can be read by this object
        """
        return False

    def __str__(self):
        """ Return the signal name.
        """
        return self.fn