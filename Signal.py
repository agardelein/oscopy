

# Signals class
class Signal:
    def __init__(self, name = "", reader = None):
        self.name = name         # Identifier
        self.reader = reader     # Reader object
        self.pts = []            # Data points
        self.ref = None          # Reference signal

    def __str__(self):
        a = self.name + " / " + (self.ref.name) + " (" + str(self.reader) + ") "
        b = ""
        if len(self.pts) > 10:
            for i in range(0, 9):
                b = b + self.pts[i] + "|"
        return a
