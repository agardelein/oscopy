
import oscopy
import gtk
import gobject
import gui
from math import log10, sqrt
from matplotlib.backend_bases import LocationEvent
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from matplotlib.widgets import SpanSelector, RectangleSelector
from matplotlib.transforms import Bbox

IOSCOPY_COL_TEXT = 0 # Combo box text
IOSCOPY_COL_X10 = 1 # x10 mode status
IOSCOPY_COL_VIS = 2 # Combobox items sensitive
IOSCOPY_COL_SPAN = 3 # Span mode status
IOSCOPY_COL_HADJ = 4 # Horizontal scrollbar adjustment
IOSCOPY_COL_VADJ = 5 # Vertical scrollbar adjustment

DEFAULT_ZOOM_FACTOR = 0.8
DEFAULT_PAN_FACTOR = 10

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
        self._draw_hid = canvas.mpl_connect('draw_event', self._update_scrollbars)
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
        hbar.connect('change-value', self.hscroll_change_value, graphs_cbx,
                     store)
        hbar.connect('enter-notify-event', self.disable_adj_update_on_draw)
        hbar.connect('leave-notify-event', self.enable_adj_update_on_draw)
        vbar.connect('change-value', self.vscroll_change_value, graphs_cbx,
                     store)
        vbar.connect('enter-notify-event', self.disable_adj_update_on_draw)
        vbar.connect('leave-notify-event', self.enable_adj_update_on_draw)
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
                self.hbar.set_sensitive(True)
                self.hbar.show()
                self.vbar.set_sensitive(False)
                self.vbar.hide()
            elif self._layout == 'vert':
                g.span = SpanSelector(g, g.onselect, 'vertical',
                                       useblit=True)
                g.span.visible = self._cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive(False)
                self.hbar.hide()
                self.vbar.set_sensitive(True)
                self.vbar.show()
            elif self._layout == 'quad':
                g.span = MyRectangleSelector(g, g.onselect, rectprops=dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True),
                                            useblit=True)
                g.span.active = self._cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive(True)
                self.hbar.show()
                self.vbar.set_sensitive(True)
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
        layout = self.layout
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
                    g = self.graphs[grnum - 1]
                    self._zoom_x10(g, a)
                    iter = store.iter_next(iter)
            else:
                g = self.graphs[grnum - 1]
                self._zoom_x10(g, a)
            self.canvas.draw_idle()

    def _zoom_x10(self, g, a):
        layout = self._layout
        result = g.dataLim.frozen()
        if layout == 'horiz' or layout == 'quad':
            g.set_xlim(*result.intervalx)
        if layout == 'vert' or layout == 'quad':
            g.set_ylim(*result.intervaly)
        if a:
            result = g.bbox.expanded(0.1, 0.1).transformed(g.transData.inverted())
            if layout == 'horiz' or layout == 'quad':
                g.set_xlim(*result.intervalx)
            if layout == 'vert' or layout == 'quad':
                g.set_ylim(*result.intervaly)

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
            if event.key == 'z':
                self._zoom_on_event(event, DEFAULT_ZOOM_FACTOR)
                self.canvas.draw_idle()
            elif event.key == 'Z':
                self._zoom_on_event(event, 1. / DEFAULT_ZOOM_FACTOR)
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

    def _zoom_on_event(self, event, factor):
        g = event.inaxes
        if g is None or factor == 1:
            return
        layout = self.layout
        result = g.bbox.expanded(factor, factor).transformed(g.transData.inverted())
        # Localisation of event.xdata in the new transform
        if layout == 'horiz' or layout == 'quad':
            g.set_xlim(*result.intervalx)
        if layout == 'vert' or layout == 'quad':
            g.set_ylim(*result.intervaly)
        # Then place it under cursor
        b = g.transData.transform_point([event.xdata, event.ydata])
        result = g.bbox.translated(-(event.x - b[0]), -(event.y - b[1])).transformed(g.transData.inverted())
        if layout == 'horiz' or layout == 'quad':
            g.set_xlim(*result.intervalx)
        if layout == 'vert' or layout == 'quad':
            g.set_ylim(*result.intervaly)
        # Limit to data boundaries
        (dxmin, dxmax) = (g.dataLim.xmin, g.dataLim.xmax)
        (xmin, xmax) = g.get_xbound()
        g.set_xbound(max(dxmin, xmin), min(dxmax, xmax))
        (dymin, dymax) = (g.dataLim.ymin, g.dataLim.ymax)
        (ymin, ymax) = g.get_ybound()
        g.set_ybound(max(dymin, ymin), min(dymax, ymax))

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
            self._zoom_on_event(event, DEFAULT_ZOOM_FACTOR)
            self.canvas.draw_idle()
        elif event.button == 'down':
            if event.inaxes is None:
                return False
            self._zoom_on_event(event, 1. / DEFAULT_ZOOM_FACTOR)
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
            self._update_graph_adj(grnum, gr)
        # Then for all graphs...

    def _update_graph_adj(self, grnum, g):
        (lower, upper) = (0, 1)

        hadj = self._cbx_store[grnum + 1][IOSCOPY_COL_HADJ]
        vadj = self._cbx_store[grnum + 1][IOSCOPY_COL_VADJ]

        # Get data Bbox and view Bbox in pixels
        (x0data, y0data, wdata, hdata) = g.dataLim.transformed(g.transData).bounds
        (xvmin, yvmin, wv, hv) = g.bbox.bounds

        # Compute page_size and value relatively to data bounds
        xpage_size = wv / wdata
        ypage_size = hv / hdata
        xvalue = (xvmin - x0data) / wdata
        yvalue = (yvmin - y0data + hv) / hdata

        xstep_increment = xpage_size / 10
        xpage_increment = xpage_size
        hadj.configure(xvalue, lower, upper,
                      xstep_increment, xpage_increment, xpage_size)
        ystep_increment = ypage_size / 10
        ypage_increment = ypage_size
        # Need to revert scroll bar to have minimum on bottom
        vadj.configure(-yvalue, -upper, lower,
                      ystep_increment, ypage_increment, ypage_size)

    def hscroll_change_value(self, widget, scroll, value, cbx, store):
        if self.layout == 'vert':
            return False
        iter = cbx.get_active_iter()
        layout = self.layout
        if iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if store.get_string_from_iter(iter) == '0':
                # Set the value for all graphs
                iter = store.iter_next(iter)
                while iter is not None:
                    grnum = int(store.get_string_from_iter(iter))
                    if grnum > len(self.graphs):
                        break
                    g = self.graphs[grnum - 1]
                    # Pan
                    iter = store.iter_next(iter)
            else:
                g = self.graphs[grnum - 1]
                # Pan
                self._translate_to(g, widget.get_value(), None)
            self.canvas.draw_idle()
        return False

    def vscroll_change_value(self, widget, scroll, value, cbx, store):
        if self.layout == 'horiz':
            return False
        iter = cbx.get_active_iter()
        layout = self.layout
        if iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if store.get_string_from_iter(iter) == '0':
                # Set the value for all graphs
                iter = store.iter_next(iter)
                while iter is not None:
                    grnum = int(store.get_string_from_iter(iter))
                    if grnum > len(self.graphs):
                        break
                    g = self.graphs[grnum - 1]
                    # Pan
                    iter = store.iter_next(iter)
            else:
                g = self.graphs[grnum - 1]
                # Pan
                self._translate_to(g, None, widget.get_value())
            self.canvas.draw_idle()
        return False

    def _translate_to(self, g, xvalue, yvalue):
        layout = self.layout

        (x0data, y0data, wdata, hdata) = g.dataLim.transformed(g.transData).bounds
        x0, y0, w, h = g.bbox.bounds
        x0_new = (xvalue * wdata + x0data) if xvalue is not None else x0
        # Need to revert scroll bar to have minimum on bottom
        y0_new = (-yvalue * hdata + y0data - h) if yvalue is not None else y0
        result = Bbox.from_bounds(x0_new, y0_new, w, h).transformed(g.transData.inverted())
        g.set_xlim(*result.intervalx)
        g.set_ylim(*result.intervaly)

    def disable_adj_update_on_draw(self, widget, event):
        layout = self.layout
        if widget == self.hbar and layout not in ['horiz', 'quad']:
            return
        if widget == self.vbar and layout not in ['vert', 'quad']:
            return
        if self._draw_hid is not None:
            self.canvas.mpl_disconnect(self._draw_hid)
            self._draw_hid = None

    def enable_adj_update_on_draw(self, widget, event):
        layout = self.layout
        if widget == self.hbar and layout not in ['horiz', 'quad']:
            return
        if widget == self.vbar and layout not in ['vert', 'quad']:
            return
        if self._draw_hid is None and not event.state & gtk.gdk.BUTTON1_MASK:
            self._draw_hid = self.canvas.mpl_connect('draw_event', self._update_scrollbars)

    layout = property(oscopy.Figure.get_layout, set_layout)
