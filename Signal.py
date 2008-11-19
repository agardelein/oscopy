

# Signals class
class Signal:
    name = ""     # Identifier for cmdline
    origfile = "" # Comes from
    origname = "" # Name as it appear in the file
    pts = []
    ref = 0       # Abscisse

    def __init__(self, name = "", origfile = "", origname = ""):
        self.name = name
        self.origfile = origfile
        self.origname = origname

    def __str__(self):
        a = self.name + " / " + " (" + self.origfile + ")"
        b = ""
        for i in range(1, 10):
            b = b + self.pts[i] + "|"
        return a + b
