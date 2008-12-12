""" Common file read functions

Class LoadFileError -- Errors encountered when loading file
   methods:
   __init__(value)
      Assign the error message

   __str__()
      Return a string with the error message

Class ReaderBase -- Define the common functions for reader objects

   methods:
   loadfile(fi)
      Check if the file can be opened before calling getsiglist(),

   getsiglist()
      To be defined into the derived objects
      Read the signals from the file, fill slist
      and return a dict of the signals, with the signame as key.

   __str__()
      Return the filename

   update()
      Reread the file and return a dict of the reread signals,
      together with a list of the updated, deleted and added signals

"""

import os.path

class LoadFileError:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "File error :", value

class ReaderBase:
    """ Reader Base -- Provide common function for signal file reading
    The derived class must redefine getsiglist()
    """
    fn = ""
    slist = []
    # Certify the path is valid and is a file
    def loadfile(self, fi):
        """ Check if the path is a valid file and call getsiglist
        """
        if fi == "":
            raise LoadFileError("No file specified")
        if not os.path.exists(fi):
            raise LoadFileError("File do not exist")
        if not os.path.isfile(fi):
            raise LoadFileError("File is not a file")
        self.fn = fi
        return self.getsiglist()

    def getsiglist(self):
        """ Read the signal list from the file, fill self.slist
        and return a dict of the signals, with the signal name as a key
        """
        return {}

    def __str__(self):
        """ Return the signal name.
        """
        return self.fn

    # Re-read the data file
    # Return signal list and names of updated, deleted and new signals
    def update(self):
        """ Reread the file, update self.slist and return a dict of the
        signals, as well as a list of the name of updated, deleted
        and new signals
        """
        u = []
        d = []
        n = []
        old = {}
        # Old signal list
        for s in self.slist:
            old[s.name] = s

        # New signal list
        sdict = self.getsiglist()

        # Find updated signals
        # Go through the old list
        for s in old.keys():
            # Signal in the new list
            if sdict.has_key(s):
                # updated signal
                u.append(s)
            else:
                # deleted signal
                d.append(s)
        # Go through the new list
        for s in sdict.keys():
            # Signal not in the old list
            if not old.has_key(s):
                #   then add
                n.append(s)
        return sdict, u, d, n
