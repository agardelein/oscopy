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
