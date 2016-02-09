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

    def make_eye(self, sn, ClockRecovery='PLL', DRsel='Auto Detect', BWsel='Auto Set'):
        [HPos, HDelay, yoff, ymult, yzero] = [0, 0, 0, 0, 0]
        xincr = self._sigs[sn].ref.data[1] - self._sigs[sn].ref.data[0]
#        print('xincr', xincr)
        ret = [1]
        [histo, adc_bins] = np.histogram(self._sigs[sn].data,
                             bins=self.Y_SAMPLING - 1,
                             density=False)
        # Digitize the signal to allow to store eye values in a matrix
        sig = np.digitize(self._sigs[sn].data, adc_bins)
        recLen = len(sig)
#        ret = self.hist(adc_bins, histo)
#        print("adc_bins", len(adc_bins), min(sig), max(sig))
        start = 0
        stop = self.Y_SAMPLING - 1
        
        # Data range, thresholds
        middle = round((start + stop) / 2)
        # The trailing [0] is needed to cover some case where condition is met
        # more than one time
        condition = histo[middle:stop] == max(histo[middle:stop])
        high = np.where(condition)[0][0] + middle
        # The trailing [0] is needed to cover some case where condition is met
        # more than one time
        condition = histo[start:middle] == max(histo[start:middle])
        low = np.where(condition)[0][0]
#        print(low, high)
        waverange = high - low
        middle = (high + low) / 2
        low_threshold = 0.3 * waverange + low
        high_threshold = 0.7 * waverange + low
#        print(low_threshold, high_threshold)

        # Find the edges
        edges = []
        greater_than_middle = sig > middle
        greater_than_high = sig > high_threshold
        lesser_than_low = sig < low_threshold
        last_gtm = greater_than_middle[0]
        cross = False
        
        for time, gtm in enumerate(greater_than_middle):
            if cross == False:
                if last_gtm != gtm:
                    last_gtm = gtm
                    edges.append(time)
                    cross = True
            else:
                if cross == greater_than_high[time] or \
                   cross == lesser_than_low[time]:
                    cross = False
#        edges = len(edges)
#        print(edges, edges)

        # Detect cycles by making edges difference
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
            cycles_durations = cycles
            bit_durations = []
            cycles_durations.sort()
            while True:
                for duration in cycles_durations:
                    if duration <= (cycles_durations[0] * 1.2):
                        bit_durations.append(duration)
                if len(bit_durations) > glitch:
                    bit_average = sum(bit_durations) / len(bit_durations)
                    break
                else:
                    cycles_durations = cycles_durations[1:]
                        
            bitrate = 1 / (bit_average * xincr)
            bit_average = int(bit_average)
        else:
            bitrate = float(DRsel)
            bit_average = int(1 / (bitrate * xincr))

        print('bitrate', bitrate, bit_average)
                
        if ClockRecovery == 'CC':
            fullrclock = []
            rclock = []
            for i in range(int(recLen * xincr * bitrate)):
                fullrclock.append(edges[0] + i * bit_average)
                swing = int(1 / (bitrate * xincr * 4))
            for a in edges: # Find corresponding edges to rclock edges
                for b in range(len(fullrclock)):
                    diff = abs(fullrclock[b] - a)
                    if swing > diff:
                        rclock.append(fullrclock[b])
                        break
        elif ClockRecovery == 'None':
            rclock = cycles
        elif ClockRecovery == 'PLL':
            fullrclock = []
            rclock = []
            for i in range(int(recLen * xincr * bitrate)):
                fullrclock.append(cycles[0] + i * bit_average)
                # find max swing from rclock to be within 2/3 of UI
            swing = 1 / (bitrate * xincr * 1.5)
            if BWsel == 'Auto Set':
                # BW filter is 1/4 data rate by default
                loopBW = 1 / (bitrate * xincr * 2)
                if loopBW < 2:
                    print('Error: Sample rate too slow to use PLL')
                    return None
            else:
                loopBW = bit_average * BWsel / bitrate
            for a in edges:
                for b, frc in enumerate(fullrclock):
                    diff = abs(frc - a)
                    if swing >= diff: # When found, filter diff and apply to rclock
                        if diff != 0:
                            filtdif = int(diff * \
                                          abs(1 / (1 + ((diff / loopBW)**2*1j))))
                            if frc > a:
                                sign = -1
                            else:
                                sign = 1
                            for d in range(b, len(rclock), 1):
                                fullrclock[d] = fullrclock[d] + sign * filtdif
                            rclock.append(frc + sign * filtdif)
                        else:
                            rclock.append(frc)
                        break

                                
#        print(fullrclock)
#        print(rclock)
        
        # Generate 2d histogram of the eye
        padsize = int(0.3 * bit_average)
        window_length = int(bit_average + 2 * padsize)
        eye = np.zeros((self.Y_SAMPLING + 1, window_length))
        for i, b in enumerate(rclock):
            window_start = b - padsize
            window_stop = b + int(bit_average + padsize)
            window = sig[window_start:window_stop]
#            print(window_start, window_stop, window)
            for a in range(len(window) - 1):
#                print(a)
                eye[window[a], a] = eye[window[a], a] + 1
#        print(eye)
        self.contourf(eye)
        
        print(start, stop)
        
        return ret
