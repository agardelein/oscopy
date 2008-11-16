

# Signals class
class Signal:
    name = ""     # Identifier for cmdline
    origfile = "" # Comes from
    origname = "" # Name as it appear in the file
    domain = ""   # Domain, time for now...

    def __str__(self):
        return self.name + " / " + self.domain + " (" + self.origfile + ")"
