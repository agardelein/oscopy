from .graph import Graph
import numpy as np

class EyeGraph(Graph):
    """ Class EyeGraph -- Draw graph with Eye scale on X and Y axis
    Based on cball code from:
    http://www1.tek.com/forum/viewtopic.php?f=5&t=4664
    """

    Y_SAMPLING = 256
    
    def __init__(self, fig, rect, sigs={}, **kwargs):
        """ Create a graph
        If signals are provided, fill in the graph otherwise the graph is empty
        Signals are assumed to exist and to be valid
        If first argument is a Graph, then copy act as a copy constructor

        Parameters
        ----------
        fig: matplotlib.figure.Figure
        Figure where to build the Graph

        rect: array of 4 floats
        Coordinates of the Graph

        sigs: dict of Signals
        List of Signals to insert once the Graph instanciated

        See also matplotlib.pyplot.Axes for list of keyword arguments

        Returns
        -------
        self: Graph
        The Graph instanciated
        """
        Graph.__init__(self, fig, rect, **kwargs)
        self._sigs = {}

        if isinstance(sigs, Graph):
            mysigs = {}
            mysigs = sigs.signals.copy()
            (self._xrange, self._yrange) = sigs.get_range()
            self._cursors = {"horiz": [None, None], "vert": [None, None]}
            self._txt = None
            self._scale_factors = sigs._scale_factors
            self._signals2lines = sigs._signals2lines.copy()
            self.insert(mysigs)
        else:
            self._xaxis = ""
            self._yaxis = ""
            self._xunit = ""
            self._yunit = ""
            self._xrange = [0, 1]
            self._yrange = [0, 1]
            # Cursors values, only two horiz and two vert but can be changed
            self._cursors = {"horiz":[None, None], "vert":[None, None]}
            self._txt = None
            self._scale_factors = [None, None]
            self._signals2lines = {}
            self.insert(sigs)
            
    @property
    def type(self):
        """ Return 'Eye', the type of the graph

        Parameter
        ---------
        None

        Returns
        -------
        string:
        The type of the graph
        """
        return "eye"

    def insert(self, sigs={}):
        """ Add a list of signals into the graph
        For Eye Graphs the list only the first element is used.
        The first signal to be added defines the abscisse.
        The remaining signals are silently ignored.
        Returns the list of ignored signals

        Parameters
        ----------
        sigs: dict of Signals
        List of Signals to be inserted in the Graph (only first one is considered)

        Returns
        -------
        rejected: dict of Signals
        List of Signals that where not inserted
        """
        rejected = {}
        for sn, s in sigs.items():
            if not self._sigs:
                # First signal, set_ the abscisse name and add signal
                self._xaxis = s.ref.name
                self._xunit = s.ref.unit
                self._yaxis = _("Signals")  # To change
                self._yunit = s.unit
                self._sigs[sn] = s
                self.set_unit((self._xunit, self._yunit))
                fx, l = self._find_scale_factor("X")
                fy, l = self._find_scale_factor("Y")
                x = s.ref.data.real * pow(10, fx)
                y = s.data.real * pow(10, fy)
                line, = self.make_eye(sn)
                self._signals2lines[sn] = line
                self._draw_cursors()
                self._print_cursors()
                self.legend()
            else:
                # Ignore signal
                rejected[sn] = s
        return rejected

    def make_eye(self, sn, ClockRecovery='CC', DRsel='Auto Detect', BWsel='Auto Set'):
        DRsel = 1e6
        sigx = self._sigs[sn].data
        sigy = self._sigs[sn].ref.data
        [HPos, HDelay, yoff, ymult, yzero] = [0, 0, 0, 0, 0]
        recLen = len(sigx)
        xincr = self._sigs[sn].ref.data[1] - self._sigs[sn].ref.data[0]
        print('xincr', xincr)
        y = np.array(self._sigs[sn].data)
#        self.hist(y, self.Y_SAMPLING)
        ret = [1]
        [histo, adc_bins] = np.histogram(self._sigs[sn].data,
                             bins=self.Y_SAMPLING,
                             density=False)
        # Digitize the signal to allow to store eye values in a matrix
        sig = np.digitize(self._sigs[sn].data, adc_bins)
#        ret = self.hist(adc_bins, histo)
#        print(adc_bins)
        start = 0
        stop = self.Y_SAMPLING - 1
        
        # Data range, thresholds
        middle = round((start + stop) / 2)
        condition = histo[middle:stop] == max(histo[middle:stop])
        # The trailing [0] is needed to cover some case where condition is met
        # more than one time
        high = adc_bins[(np.where(condition)[0]) + middle][0]
#        print(np.where(condition), adc_bins[np.where(condition)[0] + middle])
        condition = histo[start:middle] == max(histo[start:middle])
        # The trailing [0] is needed to cover some case where condition is met
        # more than one time
        low = adc_bins[(np.where(condition)[0])][0]
#        print(np.where(condition), adc_bins[np.where(condition)])
#        print(low, high)
        waverange = high - low
        middle = (high + low) / 2
        low_threshold = 0.3 * waverange + low
        high_threshold = 0.7 * waverange + low
        print(low_threshold, high_threshold)

        # Find the edges
        edges = []
        greater_than_middle = y > adc_bins[round((start + stop) / 2)]
        greater_than_high = y > high_threshold
        lesser_than_low = y < low_threshold
        temp = greater_than_middle[0]
        cross = False
        
        for a, gtm in enumerate(greater_than_middle):
            if cross == False:
                if temp != gtm:
                    temp = gtm
                    edges.append(a)
                    cross = True
            else:
                if cross == greater_than_high[a] or cross == lesser_than_low[a]:
                    cross = False

#        edges = len(edges)
#        print(edges, edges)

        # Make array of differences
        cycles = []
        for a, edge in enumerate(edges):
            try:
                cycles.append(edges[a + 1] - edge)
            except:
                pass

        # Verify that enough cycles are present to construct the eye
        if len(cycles) < 4:
            print('Not enough cycles to construct the eye')
            return [1]

        # Determine the bitrate
        if DRsel == 'Auto Detect':
            glitch = int(len(cycles) / 10)
            if glitch < 1:
                glitch = 1
            var3 = cycles
            var4 = []
            var3.sort()
            while True:
                for a in var3:
                    if a <= (var3[0] * 1.2):
                        var4.append(a)
                if len(var4) > glitch:
                    bitave = float(sum(var4) / len(var4))
                    break
                else:
                    var3 = var3[1:]
                        
            bitrate = 1 / (bitave * xincr)
            bitave = int(bitave)
        else:
            bitrate = float(DRsel)
            bitave = int(1 / (bitrate * xincr))

        print('bitrate', bitrate, bitave)
                
        if ClockRecovery == 'CC':
            fullrclock = []
            rclock = []
            for i in range(int(float(recLen) * float(xincr) * float(bitrate))):
                fullrclock.append(edges[0] + i * bitave)
                swing = int(1 / (float(bitrate) * float(xincr) * 4))
            for a in edges: # Find corresponding edges to rclock edges
                for b in range(len(fullrclock)):
                    diff = abs(fullrclock[b] - a)
                    if swing > diff:
                        rclock.append(fullrclock[b])
                        break
#        print(fullrclock)
#        print(rclock)
        
        # Generate 2d histogram of the eye
        padsize = int(0.3 * bitave)
        window_length = int(bitave + 2 * padsize)
        eye = np.zeros((self.Y_SAMPLING, window_length))
        for i, b in enumerate(rclock):
            window_start = b - padsize
            window_stop = b + int(bitave + padsize)
            window = (sigx[window_start:window_stop] - min(sigx)) / (max(sigx) - min(sigx)) * (self.Y_SAMPLING - 1)
#            print(window_start, window_stop, window)
            for a in range(len(window) - 1):
#                print(a)
                eye[window[a], a] = eye[window[a], a] + 1
#        print(eye)
        self.contourf(eye)
        
        print(start, stop)
        
        return ret
















    def old_make_eye(self):
        # Digitize the signal with resolution self.Y_SAMPLING
        mini = min(self._sigs[sn].data)
        maxi = max(self._sigs[sn].data)
        bins = np.linspace(0, self.Y_SAMPLING - 1, self.Y_SAMPLING)
        wave = np.digitize((self._sigs[sn].data - mini) / maxi * (self.Y_SAMPLING - 1), bins)
        print("wave: %d" % len(wave))
        print(bins, min(wave), max(wave))

        # Assumes the signal has discrete values, on self.Y_SAMPLING resoluton
        histo = np.arange(self.Y_SAMPLING)
        for a in range(len(histo)):
            histo[a] = 0

        # make x, y for the waveform plot
        x = self._sigs[sn].ref.data
        y = array(wave)

        # build a 1d histogram
        for a in wave:
            histo[a - 1] = histo[a - 1] + 1

        # Find the range where data starts and stops in historgram
        for a in range(self.Y_SAMPLING):
            if histo[a] != 0:
                start = a
                break
        for a in range(self.Y_SAMPLING - 1, 0, -1):
            if histo[a] != 0:
                stop = a
                break

        print(start, stop)

        return [1]
