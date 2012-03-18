
import oscopy
import gtk
import gobject
import gui
from math import log10, sqrt
from matplotlib.backend_bases import LocationEvent
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from matplotlib.widgets import SpanSelector, RectangleSelector

IOSCOPY_COL_TEXT = 0 # Combo box text
IOSCOPY_COL_X10 = 1 # x10 mode status
IOSCOPY_COL_VIS = 2 # Combobox items sensitive
IOSCOPY_COL_SPAN = 3 # Span mode status
IOSCOPY_COL_HADJ = 4 # Horizontal scrollbar adjustment
IOSCOPY_COL_VADJ = 5 # Vertical scrollbar adjustment

DEFAULT_ZOOM_FACTOR = 0.8
DEFAULT_PAN_FACTOR = 10

class Center(object):
    # Stupid class to store center coordinates when zooming
    def __init__(self):
        self.x = 0
        self.y = 0

class MyRectangleSelector(RectangleSelector):
    """ FIXME: To be removed once upstream has merged PR #658
    https://github.com/matplotlib/matplotlib/pull/658
    """ 

    def ignore(self, event):
        'return ``True`` if *event* should be ignored'
        # If RectangleSelector is not active :
        if not self.active:
            return True

        # If canvas was locked
        if not self.canvas.widgetlock.available(self):
            return True

        # Only do rectangle selection if event was triggered
        # with a desired button
        if self.validButtons is not None:
            if not event.button in self.validButtons:
                return True

        # If no button was pressed yet ignore the event if it was out
        # of the axes
        if self.eventpress == None:
            return event.inaxes!= self.ax

        # If a button was pressed, check if the release-button is the
        # same. If event is out of axis, limit the data coordinates to axes
        # boundaries.
        if event.button == self.eventpress.button and event.inaxes != self.ax:
            (xdata, ydata) = self.ax.transData.inverted().transform_point((event.x, event.y))
            x0, x1 = self.ax.get_xbound()
            y0, y1 = self.ax.get_ybound()
            xdata = max(x0, xdata)
            xdata = min(x1, xdata)
            ydata = max(y0, ydata)
            ydata = min(y1, ydata)
            event.xdata = xdata
            event.ydata = ydata
            return False

        # If a button was pressed, check if the release-button is the
        # same.
        return (event.inaxes!=self.ax or
                event.button != self.eventpress.button)

class IOscopy_GTK_Figure(oscopy.Figure):
    def __init__(self, sigs={}, fig=None, title=''):
        oscopy.Figure.__init__(self, None, fig)
        self._TARGET_TYPE_SIGNAL = 10354
        self._to_figure = [("oscopy-signals", gtk.TARGET_SAME_APP,\
                                self._TARGET_TYPE_SIGNAL)]

        w = gtk.Window()
        w.set_title(title)

        hbox1 = gtk.HBox() # The window
        vbox1 = gtk.VBox() # The Graphs
        hbox1.pack_start(vbox1)
        w.add(hbox1)
        canvas = FigureCanvas(self)
        canvas.mpl_connect('button_press_event', self._button_press)
        canvas.mpl_connect('scroll_event', self._mouse_scroll)
        canvas.mpl_connect('axes_enter_event', self._axes_enter)
        canvas.mpl_connect('axes_leave_event', self._axes_leave)
        canvas.mpl_connect('figure_enter_event', self._figure_enter)
        canvas.mpl_connect('figure_leave_event', self._figure_leave)
        canvas.mpl_connect('key_press_event', self._key_press)
        canvas.mpl_connect('draw_event', self._update_scrollbars)
        w.connect('delete-event', lambda w, e: w.hide() or True)
        w.drag_dest_set(gtk.DEST_DEFAULT_MOTION |\
                                 gtk.DEST_DEFAULT_HIGHLIGHT |\
                                 gtk.DEST_DEFAULT_DROP,
                             self._to_figure, gtk.gdk.ACTION_COPY)

        hbar = gtk.HScrollbar()
        hbar.set_sensitive(False)
        self.hbar = hbar
        vbox1.pack_start(hbar, False, False)
        vbar = gtk.VScrollbar()
        vbar.set_sensitive(False)
        self.vbar = vbar
        hbox1.pack_start(vbar, False, False)

        vbox1.pack_start(canvas)

        toolbar = NavigationToolbar(canvas, w)
        vbox1.pack_start(toolbar, False, False)

        vbox2 = gtk.VBox() # The right-side menu
        store = gtk.ListStore(gobject.TYPE_STRING, # String displayed
                              gobject.TYPE_BOOLEAN, # x10 mode status
                              gobject.TYPE_BOOLEAN, # Combobox item sensitive
                              gobject.TYPE_BOOLEAN, # Span mode status
                              gobject.TYPE_PYOBJECT, # Horizontal Adjustment
                              gobject.TYPE_PYOBJECT, # Vertical Adjustment
                              )
        iter = store.append([_('All Graphs'), False, True, False, gtk.Adjustment(), gtk.Adjustment()])
        for i in xrange(4):
            iter = store.append([_('Graph %d') % (i + 1), False, True if i < len(self.graphs) else False, False, gtk.Adjustment(), gtk.Adjustment()])
        self._cbx_store = store

        graphs_cbx = gtk.ComboBox(store)
        cell = gtk.CellRendererText()
        graphs_cbx.pack_start(cell, True)
        graphs_cbx.add_attribute(cell, 'text', IOSCOPY_COL_TEXT)
        graphs_cbx.add_attribute(cell, 'sensitive', IOSCOPY_COL_VIS)
        graphs_cbx.set_active(0)
        vbox2.pack_start(graphs_cbx, False, False)

        x10_toggle_btn = gtk.ToggleButton('x10 mode')
        x10_toggle_btn.set_mode(True)
        x10_toggle_btn.connect('toggled', self.x10_toggle_btn_toggled,
                               graphs_cbx, store)

        span_toggle_btn = gtk.ToggleButton(_('Span'))
        span_toggle_btn.set_mode(True)
        span_toggle_btn.connect('toggled', self.span_toggle_btn_toggled,
                               graphs_cbx, store)

        self._cbx = graphs_cbx
        self._btn = x10_toggle_btn

        graphs_cbx.connect('changed', self.graphs_cbx_changed, x10_toggle_btn,
                           span_toggle_btn, store)
        vbox2.pack_start(x10_toggle_btn, False, False)
        vbox2.pack_start(span_toggle_btn, False, False)

        hbox1.pack_start(vbox2, False, False)

        w.resize(640, 480)
        w.show_all()
        self.window = w
        if sigs:
            self.add(sigs)
#        # Update canvas for SpanSelector of Graphs
        for gr in self.graphs:
            if hasattr(gr, 'span'):
                gr.span.new_axes(gr)

    def set_layout(self, layout='quad'):
        oscopy.Figure.set_layout(self, layout)
        iter = self._cbx_store.get_iter_first()
        for g in self.graphs:
            iter = self._cbx_store.iter_next(iter)
            if self._layout == 'horiz':
                g.span = SpanSelector(g, g.onselect, 'horizontal',
                                       useblit=True)
                g.span.visible = self._cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive = True
                self.hbar.show()
                self.vbar.set_sensitive = False
                self.vbar.hide()
            elif self._layout == 'vert':
                g.span = SpanSelector(g, g.onselect, 'vertical',
                                       useblit=True)
                g.span.visible = self._cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive = False
                self.hbar.hide()
                self.vbar.set_sensitive = True
                self.vbar.show()
            elif self._layout == 'quad':
                g.span = MyRectangleSelector(g, g.onselect, rectprops=dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True),
                                            useblit=True)
                g.span.active = self._cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive = True
                self.hbar.show()
                self.vbar.set_sensitive = True                
                self.vbar.show()

    def graphs_cbx_changed(self, graphs_cbx, x10_toggle_btn, span_toggle_btn, store):
        iter = graphs_cbx.get_active_iter()
        if store.get_string_from_iter(iter) == '0':
            # Do all the graphs have same state?
            store.iter_next(iter)
            val = store.get_value(iter, IOSCOPY_COL_X10)
            while iter is not None:
                if val != store.get_value(iter, IOSCOPY_COL_X10):
                    # Yes, set the button into inconsistent state
                    x10_toggle_btn.set_inconsistent(True)
                    break
                iter = store.iter_next(iter)
            iter = store.get_iter_first()
            store.iter_next(iter)
            val = store.get_value(iter, IOSCOPY_COL_SPAN)
            while iter is not None:
                if val != store.get_value(iter, IOSCOPY_COL_SPAN):
                    # Yes, set the button into inconsistent state
                    span_toggle_btn.set_inconsistent(True)
                    break
                iter = store.iter_next(iter)
            self.hbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_HADJ))
            self.vbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_VADJ))
        else:
            x10_toggle_btn.set_inconsistent(False)
            x10_toggle_btn.set_active(store.get_value(iter, IOSCOPY_COL_X10))
            span_toggle_btn.set_inconsistent(False)
            span_toggle_btn.set_active(store.get_value(iter, IOSCOPY_COL_SPAN))
            self.hbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_HADJ))
            self.vbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_VADJ))
            
    def x10_toggle_btn_toggled(self, x10_toggle_btn, graphs_cbx, store):
        center = None
        iter = graphs_cbx.get_active_iter()
        a = x10_toggle_btn.get_active()
        val = -.1 if a else -1           # x10 zoom
        x10_toggle_btn.set_inconsistent(False)
        if iter is not None:
            store.set_value(iter, IOSCOPY_COL_X10, a)
            grnum = int(store.get_string_from_iter(iter))
            if store.get_string_from_iter(iter) == '0':
                # Set the value for all graphs
                iter = store.iter_next(iter)
                while iter is not None:
                    store.set_value(iter, IOSCOPY_COL_X10, a)
                    grnum = int(store.get_string_from_iter(iter))
                    if grnum > len(self.graphs):
                        break
                    self._zoom(grnum, center, val)
                    iter = store.iter_next(iter)
            else:
                self._zoom(grnum, center, val)
            self.canvas.draw()

    def span_toggle_btn_toggled(self, span_toggle_btn, graphs_cbx, store):
        iter = graphs_cbx.get_active_iter()
        a = span_toggle_btn.get_active()
        span_toggle_btn.set_inconsistent(False)
        if iter is not None:
            store.set_value(iter, IOSCOPY_COL_SPAN, a)
            grnum = int(store.get_string_from_iter(iter))
            if store.get_string_from_iter(iter) == '0':
                # Set the value for all graphs
                iter = store.iter_next(iter)
                while iter is not None:
                    store.set_value(iter, IOSCOPY_COL_SPAN, a)
                    grnum = int(store.get_string_from_iter(iter))
                    if grnum > len(self.graphs):
                        break
                    if hasattr(self.graphs[grnum - 1].span, 'active'):
                        self.graphs[grnum - 1].span.active = a
                    elif hasattr(self.graphs[grnum - 1].span, 'visible'):
                        self.graphs[grnum - 1].span.visible = a
                    iter = store.iter_next(iter)
            else:
                if hasattr(self.graphs[grnum - 1].span, 'active'):
                    self.graphs[grnum - 1].span.active = a
                elif hasattr(self.graphs[grnum - 1].span, 'visible'):
                    self.graphs[grnum - 1].span.visible = a
            self.canvas.draw()

    def _key_press(self, event):
        if event.inaxes is not None:
            g = event.inaxes
            grnum = self.graphs.index(g) + 1
            center = Center()
            center.x = event.xdata
            center.y = event.ydata
            if event.key == 'z':
                self._zoom(grnum, center, DEFAULT_ZOOM_FACTOR)
                self.canvas.draw_idle()
            elif event.key == 'Z':
                self._zoom(grnum, center, 1 / DEFAULT_ZOOM_FACTOR)
                self.canvas.draw_idle()
            elif event.key == 'l':
                result = g.bbox.translated(-DEFAULT_PAN_FACTOR, 0).transformed(g.transData.inverted())
                g.set_xlim(*result.intervalx)
                g.set_ylim(*result.intervaly)
                self.canvas.draw_idle()
            elif event.key == 'r':
                result = g.bbox.translated(DEFAULT_PAN_FACTOR, 0).transformed(g.transData.inverted())
                g.set_xlim(*result.intervalx)
                g.set_ylim(*result.intervaly)
                self.canvas.draw_idle()
        return True

    def _zoom(self, grnum, center=None, factor=1):
        # In which layout are we (horiz, vert, quad ?)
        layout = self.layout
        gr = self.graphs[grnum - 1]
        [xmin, xmax, ymin, ymax] = [None for x in xrange(4)]
        [(xmin_cur, xmax_cur), (ymin_cur, ymax_cur)] = gr.range
        [(xmin_new, xmax_new), (ymin_new, ymax_new)] = gr.range

        # Get the bounds of the data (min, max)
        if layout == 'horiz' or layout == 'quad':
            (xmin, xmax) = (gr.dataLim.xmin, gr.dataLim.xmax)

        if layout == 'vert' or layout == 'quad':
            (ymin, ymax) = (gr.dataLim.ymin, gr.dataLim.ymax)

        # Calculate the x10 (linear or log scale ?) and set it
        sc = gr.scale
        logx = True if sc == 'logx' or sc == 'loglog' else False
        logy = True if sc == 'logy' or sc == 'loglog' else False
        if xmin is not None and xmax is not None:
            if logx:
                cx = log10(center.x) if center is not None else None
                curb = (log10(xmin_cur), log10(xmax_cur)) # Current bounds
                datab = (log10(xmin), log10(xmax))        # Data bounds
                newb = self._compute_zoom_range(curb, datab, cx, factor)
                (xmin_new, xmax_new) = newb               # New bounds
                xmin_new = pow(10, xmin_new)
                xmax_new = pow(10, xmax_new)
            else:
                cx = center.x if center is not None else None
                curb = (xmin_cur, xmax_cur) # Current bounds
                datab = (xmin, xmax)        # Data bounds
                newb = self._compute_zoom_range(curb, datab, cx, factor)
                (xmin_new, xmax_new) = newb # New bounds
            gr.set_xbound(xmin_new, xmax_new)

        if ymin is not None and ymax is not None:
            if logy:
                cy = log10(center.y) if center is not None else None
                curb = (log10(ymin_cur), log10(ymax_cur)) # Current bounds
                datab = (log10(ymin), log10(ymax))        # Data bounds
                newb = self._compute_zoom_range(curb, datab, cy, factor)
                (ymin_new, ymax_new) = newb               # New bounds
                ymin_new = pow(10, ymin_new)
                ymax_new = pow(10, ymax_new)
            else:
                cy = center.y if center is not None else None
                curb = (ymin_cur, ymax_cur) # Current bounds
                datab = (ymin, ymax)        # Data bounds
                newb = self._compute_zoom_range(curb, datab, cy, factor)
                (ymin_new, ymax_new) = newb # New bounds
            gr.set_ybound(ymin_new, ymax_new)

    def _compute_zoom_range(self, curb, datab, center=None, factor=-1):
        # Zoom is relative to current bounds when factor > 0
        # otherwise is relative to data bounds
        if not factor:
            return curb
        (data_min, data_max) = datab
        (min_cur, max_cur) = curb if factor > 0 else datab
        if factor == -1:
            return (data_min, data_max)
        curf = (max_cur - min_cur) / (data_max - data_min)
        factor = factor * curf
        if factor > 1:
            return (data_min, data_max)
        if center is None:
            center = (max_cur + min_cur) / 2
        pos = (center - min_cur) / (max_cur - min_cur)
        min_new = center - (data_max - data_min) * (abs(factor) * pos)
        max_new = center + (data_max - data_min) * (abs(factor) * (1 - pos))
        if min_new < data_min:
            max_new = max_new + (data_min - min_new)
            min_new = data_min
        if max_new > data_max:
            min_new = min_new + (data_max - max_new)
            max_new = data_max
        if min_new > max_new:
            return (max_new, min_new)
        else:
            return (min_new, max_new)

    def drag_data_received_cb(self, widget, drag_context, x, y, selection,\
                                   target_type, time, ctxtsignals):
        # Event handling issue: this drag and drop callback is
        # processed before matplotlib callback _axes_enter. Therefore
        # when dropping, self._current_graph is not valid: it contains
        # the last graph.
        # The workaround is to retrieve the Graph by creating a Matplotlib
        # LocationEvent considering inverse 'y' coordinates
        if target_type == self._TARGET_TYPE_SIGNAL:
            canvas = self.canvas
            my_y = canvas.allocation.height - y
            event = LocationEvent('axes_enter_event', canvas, x, my_y)
            signals = {}
            for name in selection.data.split():
                signals[name] = ctxtsignals[name]
            if event.inaxes is not None:
                # Graph not found
                event.inaxes.insert(signals)
                self.canvas.draw()

    def add(self, args):
        oscopy.Figure.add(self, args)
        store = self._cbx_store
        iter = store.get_iter_first()
        iter = store.iter_next(iter)  # First item always sensitive
        while iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if grnum > len(self.graphs):
                store.set_value(iter, IOSCOPY_COL_VIS, False)
            else:
                store.set_value(iter, IOSCOPY_COL_VIS, True)
            iter = store.iter_next(iter)       

    def delete(self, args):
        oscopy.Figure.delete(self, args)
        store = self._cbx_store
        iter = store.get_iter_first()
        iter = store.iter_next(iter)  # First item always sensitive
        while iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if grnum > len(self.graphs):
                store.set_value(iter, IOSCOPY_COL_VIS, False)
            else:
                store.set_value(iter, IOSCOPY_COL_VIS, True)
            iter = store.iter_next(iter)       

    def _button_press(self, event):
        if event.button == 3:
            menu = self._create_figure_popup_menu(event.canvas.figure, event.inaxes)
            menu.show_all()
            menu.popup(None, None, None, event.button, event.guiEvent.time)

    def _mouse_scroll(self, event):
        if event.button == 'up':
            if event.inaxes is None:
                return False
            g = event.inaxes
            grnum = self.graphs.index(g) + 1
            center = Center()
            center.x = event.xdata
            center.y = event.ydata
            self._zoom(grnum, center, DEFAULT_ZOOM_FACTOR)
            self.canvas.draw_idle()
        elif event.button == 'down':
            if event.inaxes is None:
                return False
            g = event.inaxes
            grnum = self.graphs.index(g) + 1
            center = Center()
            center.x = event.xdata
            center.y = event.ydata
            self._zoom(grnum, center, 1. / DEFAULT_ZOOM_FACTOR)
            self.canvas.draw_idle()
        return True

    def _axes_enter(self, event):
#        self._figure_enter(event)
#        self._current_graph = event.inaxes

#        axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
#        fig_num = self._ctxt.figures.index(self._current_figure) + 1
#        self._app_exec('%%oselect %d-%d' % (fig_num, axes_num))
        pass

    def _axes_leave(self, event):
        # Unused for better user interaction
#        self._current_graph = None
        pass

    def _figure_enter(self, event):
#        self._current_figure = event.canvas.figure
#        if hasattr(event, 'inaxes') and event.inaxes is not None:
#            axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
#        else:
#            axes_num = 1
#        fig_num = self._ctxt.figures.index(self._current_figure) + 1
#        self._app_exec('%%oselect %d-%d' % (fig_num, axes_num))
        self.canvas.grab_focus()
        pass

    def _figure_leave(self, event):
#        self._current_figure = None
        pass

    def _create_figure_popup_menu(self, figure, graph):
        figmenu = gui.menus.FigureMenu()
        return figmenu.create_menu(figure, graph)

    def _update_scrollbars(self, event):
        for grnum, gr in enumerate(self.graphs):
            self._update_graph_adj(grnum + 1, gr)
        # Then for all graphs...

    def _update_graph_adj(self, grnum, gr):
        layout = self.layout
        [xmin, xmax, ymin, ymax] = [None for x in xrange(4)]
        [(xmin_cur, xmax_cur), (ymin_cur, ymax_cur)] = gr.range
        [(xmin_new, xmax_new), (ymin_new, ymax_new)] = gr.range

        # Get the bounds of the data (min, max)
        if layout == 'horiz' or layout == 'quad':
            (xmin, xmax) = (gr.dataLim.xmin, gr.dataLim.xmax)

        if layout == 'vert' or layout == 'quad':
            (ymin, ymax) = (gr.dataLim.ymin, gr.dataLim.ymax)

        # Calculate the x10 (linear or log scale ?) and set it
        sc = gr.scale
        logx = True if sc == 'logx' or sc == 'loglog' else False
        logy = True if sc == 'logy' or sc == 'loglog' else False
        if xmin is not None and xmax is not None:
            if logx:
                curb = (log10(xmin_cur), log10(xmax_cur)) # Current bounds
                datab = (log10(xmin), log10(xmax))        # Data bounds
            else:
                curb = (xmin_cur, xmax_cur) # Current bounds
                datab = (xmin, xmax)        # Data bounds
            adj = self._cbx_store[grnum][IOSCOPY_COL_HADJ]
            self._update_adjustment(adj, curb, datab)

        if ymin is not None and ymax is not None:
            if logy:
                curb = (log10(ymin_cur), log10(ymax_cur)) # Current bounds
                datab = (log10(ymin), log10(ymax))        # Data bounds
            else:
                curb = (ymin_cur, ymax_cur) # Current bounds
                datab = (ymin, ymax)        # Data bounds
            adj = self._cbx_store[grnum][IOSCOPY_COL_VADJ]
            self._update_adjustment(adj, curb, datab)

    def _update_adjustment(self, adj, curb, datab):
        (lower, upper) = datab
        (cmin, cmax) = curb
        value = (cmin + cmax) / 2
        page_size = (cmax - cmin)
        step_increment = page_size / 10
        page_increment = page_size
        adj.configure(value, lower, upper, step_increment, page_increment,
                      page_size)

    layout = property(oscopy.Figure.get_layout, set_layout)
