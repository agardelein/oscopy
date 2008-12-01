from Axe import Axe

class Graph:
#    mode = "scal"
#    axex = 0
#    axey = 0
#    sigs = {}
#    xaxis = ""

    # Create axis, and fill them with data
    def __init__(self, sigs = None, mode = "scal"):
        # Here signals do exist and are valid
        self.mode = mode
        self.sigs = {}
        self.xaxis = ""
        if sigs == None:
            return
        else:
            print len(self.sigs)
            self.add(sigs)
            return

    def add(self, sigs = None):
        print len(sigs), len(self.sigs)
        if sigs == None:
            return
        for s in sigs:
            if len(self.sigs) == 0:
                self.xaxis = s.ref.name
                self.sigs[s.name] = s
            else:
                if s.ref.name == self.xaxis:
                    self.sigs[s.name] = s
                else:
                    print "Not the same ref:", s.name, "-", self.xaxis,"-"

    def setg(self, sigs = None):
        print "yoo"
        self.sigs = {}
        self.xaxis = ""
        self.add(sigs)

    def plot(self):
        a = 1

    def __str__(self):
        a = self.mode + " "
        print len(self.sigs)
        for n, s in self.sigs.iteritems():
            a = a + n
            a = a + " "
        return a
