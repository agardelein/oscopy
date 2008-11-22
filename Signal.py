

# Signals class
class Signal:
    name = ""     # Identifier for cmdline
    reader = None # Comes from
    pts = []
    ref = None       # Abscisse

    def __init__(self, name = "", reader = None):
        self.name = name
        self.reader = reader
        self.pts = []

    def __str__(self):
        a = self.name + " / (" + str(self.reader) + ") "
        b = ""
        if len(self.pts) > 10:
            for i in range(0, 9):
                b = b + self.pts[i] + "|"
        return a + b
