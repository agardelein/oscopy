import os.path
from ExceptErrors import *

class ReaderBase:
    fn = ""
    slist = []
    # Certify the path is valid and is a file
    def loadfile(self, fi):
        if fi == "":
            raise LoadFileError("No file specified")
        if not os.path.exists(fi):
            raise LoadFileError("File do not exist")
        if not os.path.isfile(fi):
            raise LoadFileError("File is not a file")
        self.fn = fi
        return self.getsiglist()

    def __str__(self):
        return self.fn

    # Re-read the data file
    # Return signal list and names of updated, deleted and new signals
    def update(self):
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
                # update signal
                u.append(s)
            else:
                # delete signal
                d.append(s)
        # Go through the new list
        for s in sdict.keys():
            # Signal not in the old list
            if not old.has_key(s):
                #   then add
                n.append(s)
        return sdict, u, d, n
