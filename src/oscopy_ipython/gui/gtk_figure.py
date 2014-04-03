
import oscopy
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from math import log10, sqrt
from matplotlib.backend_bases import LocationEvent
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import FileChooserDialog
from matplotlib.widgets import SpanSelector, RectangleSelector
from matplotlib.transforms import Bbox

IOSCOPY_COL_TEXT = 0 # Combo box text
IOSCOPY_COL_X10 = 1 # x10 mode status
IOSCOPY_COL_VIS = 2 # Combobox items sensitive
IOSCOPY_COL_SPAN = 3 # Span mode status
IOSCOPY_COL_HADJ = 4 # Horizontal scrollbar adjustment
IOSCOPY_COL_VADJ = 5 # Vertical scrollbar adjustment

IOSCOPY_GTK_FIGURE_UI = 'oscopy/gtk_figure.glade'

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
    def __init__(self, sigs={}, fig=None, title='', uidir=''):
        oscopy.Figure.__init__(self, None, fig)
        self.TARGET_TYPE_SIGNAL = 10354
        self.to_figure = [Gtk.TargetEntry.new("oscopy-signals", Gtk.TargetFlags.SAME_APP,\
                                self.TARGET_TYPE_SIGNAL)]
        self.hadjpreval = None
        self.vadjpreval = None

        # The canvas for the Figure
        canvas = FigureCanvas(self)
        canvas.supports_blit = False
        canvas.mpl_connect('button_press_event', self.button_press)
        canvas.mpl_connect('scroll_event', self.mouse_scroll)
        canvas.mpl_connect('axes_enter_event', self.axes_enter)
        canvas.mpl_connect('axes_leave_event', self.axes_leave)
        canvas.mpl_connect('figure_enter_event', self.figure_enter)
        canvas.mpl_connect('figure_leave_event', self.figure_leave)
        canvas.mpl_connect('key_press_event', self.key_press)
        canvas.mpl_connect('motion_notify_event', self.show_coords)
        self.canvas = canvas
        self.draw_hid = canvas.mpl_connect('draw_event', self.update_scrollbars)

        # The store for the combo box
        store = Gtk.ListStore(GObject.TYPE_STRING, # String displayed
                              GObject.TYPE_BOOLEAN, # x10 mode status
                              GObject.TYPE_BOOLEAN, # Combobox item sensitive
                              GObject.TYPE_BOOLEAN, # Span mode status
                              GObject.TYPE_PYOBJECT, # Horizontal Adjustment
                              GObject.TYPE_PYOBJECT, # Vertical Adjustment
                              )
        iter = store.append([_('All Graphs'), False, True, False, Gtk.Adjustment(), Gtk.Adjustment()])
        for i in range(4):
            iter = store.append([_('Graph %d') % (i + 1), False, True if i < len(self.graphs) else False, False, Gtk.Adjustment(), Gtk.Adjustment()])
        self.cbx_store = store

        # The Graph Combobox
        graphs_cbx = Gtk.ComboBox.new_with_model(store)
        cell = Gtk.CellRendererText()
        graphs_cbx.pack_start(cell, True)
        graphs_cbx.add_attribute(cell, 'text', IOSCOPY_COL_TEXT)
        graphs_cbx.add_attribute(cell, 'sensitive', IOSCOPY_COL_VIS)
        graphs_cbx.set_active(0)

        # The GtkBuilder
        builder = Gtk.Builder()
        builder.expose_object('store', self.cbx_store)
        builder.add_from_file('/'.join((uidir, IOSCOPY_GTK_FIGURE_UI)))
        self.builder = builder

        # Add remaining widgets
        builder.get_object('box').pack_start(canvas, True, True, 0)
        builder.get_object('buttonbar').pack_start(graphs_cbx, False, False, 0)
        builder.get_object('buttonbar').reorder_child(graphs_cbx, 0)

        # Expose widgets needed elsewhere
        self.window = builder.get_object('w')
        self.hbar = builder.get_object('hbar')
        self.vbar = builder.get_object('vbar')
        self.coords_lbl1 = builder.get_object('coord_lbl1')
        self.coords_lbl2 = builder.get_object('coord_lbl2')
        self.graphs_cbx = graphs_cbx
        self.store = store
        self.mpsel_get_act = [builder.get_object('rb%d' % (b + 1)).get_active for b in range(4)]
        self.mpsel_set_act = [builder.get_object('rb%d' % (b + 1)).set_active for b in range(4)]
        self.mpsel_set_sens = [builder.get_object('rb%d' % (b + 1)).set_sensitive for b in range(4)]
        self.window.show_all()

        # Connect additional GTK signals
        cbmap = {'span_toggle_btn_toggled': self.span_toggle_btn_toggled,
                 'x10_toggle_btn_toggled': self.x10_toggle_btn_toggled,
                 'hadj_pressed': self.hadj_pressed,
                 'hadj_released': self.hadj_released,
                 'hscroll_change_value': self.hscroll_change_value,
                 'vadj_pressed': self.vadj_pressed,
                 'vadj_released': self.vadj_released,
                 'vscroll_change_value': self.vscroll_change_value,
                 'disable_adj_update_on_draw': self.disable_adj_update_on_draw,
                 'enable_adj_update_on_draw': self.enable_adj_update_on_draw,
                 'update_scrollbars': self.update_scrollbars,
                 'save_fig_btn_clicked': self.save_fig_btn_clicked,
                 }
        builder.connect_signals(cbmap)
        graphs_cbx.connect('changed', self.graphs_cbx_changed,
                           (builder.get_object('x10_toggle_btn'),
                            builder.get_object('span_toggle_btn'),
                            store))

        # Add signals
        if sigs:
            self.add(sigs)
#        # Update canvas for SpanSelector of Graphs
        for gr in self.graphs:
            if hasattr(gr, 'span'):
                gr.span.new_axes(gr)

    def delete_me(self, sigs={}, fig=None, title=''):

        w = Gtk.Window()
        w.set_title(title)

        hbox1 = Gtk.HBox() # The window
        vbox1 = Gtk.VBox() # The Graphs
        hbox1.pack_start(vbox1, True, True, 0)
        w.add(hbox1)
        canvas = FigureCanvas(self)
        canvas.supports_blit = False
        canvas.mpl_connect('button_press_event', self._button_press)
        canvas.mpl_connect('scroll_event', self._mouse_scroll)
        canvas.mpl_connect('axes_enter_event', self._axes_enter)
        canvas.mpl_connect('axes_leave_event', self._axes_leave)
        canvas.mpl_connect('figure_enter_event', self._figure_enter)
        canvas.mpl_connect('figure_leave_event', self._figure_leave)
        canvas.mpl_connect('key_press_event', self._key_press)
        canvas.mpl_connect('motion_notify_event', self._show_coords)
        self.draw_hid = canvas.mpl_connect('draw_event', self._update_scrollbars)
        w.connect('delete-event', lambda w, e: w.hide() or True)
        w.drag_dest_set(Gtk.DestDefaults.MOTION |\
                                 Gtk.DestDefaults.HIGHLIGHT |\
                                 Gtk.DestDefaults.DROP,
                             self._to_figure, Gdk.DragAction.COPY)

        hbar = Gtk.HScrollbar()
        hbar.set_sensitive(False)
        self.hbar = hbar
        vbox1.pack_start(hbar, False, False, 0)
        vbar = Gtk.VScrollbar()
        vbar.set_sensitive(False)
        self.vbar = vbar
        hbox1.pack_start(vbar, False, False, 0)

        vbox1.pack_start(canvas, True, True, 0)

        vbox2 = Gtk.VBox() # The right-side menu
        store = Gtk.ListStore(GObject.TYPE_STRING, # String displayed
                              GObject.TYPE_BOOLEAN, # x10 mode status
                              GObject.TYPE_BOOLEAN, # Combobox item sensitive
                              GObject.TYPE_BOOLEAN, # Span mode status
                              GObject.TYPE_PYOBJECT, # Horizontal Adjustment
                              GObject.TYPE_PYOBJECT, # Vertical Adjustment
                              )
        iter = store.append([_('All Graphs'), False, True, False, Gtk.Adjustment(), Gtk.Adjustment()])
        for i in range(4):
            iter = store.append([_('Graph %d') % (i + 1), False, True if i < len(self.graphs) else False, False, Gtk.Adjustment(), Gtk.Adjustment()])
        self.cbx_store = store
        hbar.set_adjustment(store[0][IOSCOPY_COL_HADJ])
        vbar.set_adjustment(store[0][IOSCOPY_COL_VADJ])

        graphs_cbx = Gtk.ComboBox.new_with_model(store)
        cell = Gtk.CellRendererText()
        graphs_cbx.pack_start(cell, True)
        graphs_cbx.add_attribute(cell, 'text', IOSCOPY_COL_TEXT)
        graphs_cbx.add_attribute(cell, 'sensitive', IOSCOPY_COL_VIS)
        graphs_cbx.set_active(0)
        vbox2.pack_start(graphs_cbx, False, False, 0)

        # master pan radiobuttons
        label = Gtk.Label(label='master pan')
        vbox2.pack_start(label, False, False, 0)

        rbtns = [Gtk.RadioButton(None, '%d' % (i + 1)) for i in range(4)]
        rbtnbox = Gtk.HBox()
        for rb in rbtns[1:4]: rb.join_group(rbtns[0])
        for rb in rbtns:
            rb.set_sensitive(False)
            rbtnbox.pack_start(rb, True, True, 0)
        # Cache the methods
        self.mpsel_get_act = [b.get_active for b in rbtns]
        self.mpsel_set_act = [b.set_active for b in rbtns]
        self.mpsel_set_sens = [b.set_sensitive for b in rbtns]
        for b in rbtns:
            b.connect('toggled', self._update_scrollbars)
        vbox2.pack_start(rbtnbox, False, False, 0)

        vbox2.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        x10_toggle_btn = Gtk.ToggleButton('x10 mode')
        x10_toggle_btn.set_mode(True)
        x10_toggle_btn.connect('toggled', self.x10_toggle_btn_toggled,
                               graphs_cbx, store)

        span_toggle_btn = Gtk.ToggleButton(_('Span'))
        span_toggle_btn.set_mode(True)
        span_toggle_btn.connect('toggled', self.span_toggle_btn_toggled,
                               graphs_cbx, store)

        save_fig_btn = Gtk.Button(_('Export'))
        save_fig_btn.connect('clicked', self.save_fig_btn_clicked)

        coords_lbl1 = Gtk.Label(label='')
        coords_lbl1.set_alignment(0.1, 0.5)
        coords_lbl2 = Gtk.Label(label='')
        coords_lbl2.set_alignment(0.1, 0.5)

        self._cbx = graphs_cbx
        self._btn = x10_toggle_btn
        self.coords_lbl1 = coords_lbl1
        self.coords_lbl2 = coords_lbl2

        graphs_cbx.connect('changed', self.graphs_cbx_changed, x10_toggle_btn,
                           span_toggle_btn, store)
        hbar.connect('change-value', self.hscroll_change_value, graphs_cbx,
                     store)
        hbar.connect('enter-notify-event', self.disable_adj_update_on_draw)
        hbar.connect('leave-notify-event', self.enable_adj_update_on_draw)
        hbar.connect('button-press-event', self.hadj_pressed)
        hbar.connect('button-release-event', self.hadj_released)
        vbar.connect('change-value', self.vscroll_change_value, graphs_cbx,
                     store)
        vbar.connect('enter-notify-event', self.disable_adj_update_on_draw)
        vbar.connect('leave-notify-event', self.enable_adj_update_on_draw)
        vbar.connect('button-press-event', self.vadj_pressed)
        vbar.connect('button-release-event', self.vadj_released)
        vbox2.pack_start(x10_toggle_btn, False, False, 0)
        vbox2.pack_start(span_toggle_btn, False, False, 0)
        vbox2.pack_start(save_fig_btn, False, False, 0)
        vbox2.pack_end(coords_lbl1, False, False, 0)
        vbox2.pack_end(coords_lbl2, False, False, 0)

        hbox1.pack_start(vbox2, False, False, 0)

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
        iter = self.cbx_store.get_iter_first()
        for g in self.graphs:
            iter = self.cbx_store.iter_next(iter)
            if self._layout == 'horiz':
                g.span = SpanSelector(g, g.onselect, 'horizontal',
                                       useblit=True)
                g.span.visible = self.cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive(True)
                self.hbar.show()
                self.vbar.set_sensitive(False)
                self.vbar.hide()
            elif self._layout == 'vert':
                g.span = SpanSelector(g, g.onselect, 'vertical',
                                       useblit=True)
                g.span.visible = self.cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive(False)
                self.hbar.hide()
                self.vbar.set_sensitive(True)
                self.vbar.show()
            elif self._layout == 'quad':
                g.span = MyRectangleSelector(g, g.onselect, rectprops=dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True),
                                            useblit=True)
                g.span.active = self.cbx_store.get_value(iter, IOSCOPY_COL_SPAN)
                self.hbar.set_sensitive(True)
                self.hbar.show()
                self.vbar.set_sensitive(True)
                self.vbar.show()

    def graphs_cbx_changed(self, graphs_cbx, data):
        (x10_toggle_btn, span_toggle_btn, store) = data
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
            self.hbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_HADJ))
            self.vbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_VADJ))
            while iter is not None:
                if val != store.get_value(iter, IOSCOPY_COL_SPAN):
                    # Yes, set the button into inconsistent state
                    span_toggle_btn.set_inconsistent(True)
                    break
                iter = store.iter_next(iter)
        else:
            x10_toggle_btn.set_inconsistent(False)
            x10_toggle_btn.set_active(store.get_value(iter, IOSCOPY_COL_X10))
            span_toggle_btn.set_inconsistent(False)
            span_toggle_btn.set_active(store.get_value(iter, IOSCOPY_COL_SPAN))
            self.hbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_HADJ))
            self.vbar.set_adjustment(store.get_value(iter, IOSCOPY_COL_VADJ))
            
    def x10_toggle_btn_toggled(self, x10_toggle_btn):
        (graphs_cbx, store) = (self.graphs_cbx, self.store)
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

    def span_toggle_btn_toggled(self, span_toggle_btn):
        (graphs_cbx, store) = (self.graphs_cbx, self.store)
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

    def save_fig_btn_clicked(self, save_fig_btn):
        fname, format = self.get_filechooser().get_filename_from_user()
        if fname:
            try:
                self.canvas.print_figure(fname, format=format)
            except Exception as e:
                error_msg_gtk(str(e), parent=self)

    def get_filechooser(self):
        # From matplotlib/backends/backend_Gtk.py
        return FileChooserDialog(
            title=_('Save the figure'),
            parent=self.window,
            filetypes=self.canvas.get_supported_filetypes(),
            default_filetype=self.canvas.get_default_filetype())

    def key_press(self, event):
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
        store = self.cbx_store
        iter = store.get_iter_first()
        iter = store.iter_next(iter)  # First item always sensitive
        while iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if grnum > len(self.graphs):
                store.set_value(iter, IOSCOPY_COL_VIS, False)
                self.mpsel_set_sens[grnum - 1](False) # master pan
            else:
                store.set_value(iter, IOSCOPY_COL_VIS, True)
                self.mpsel_set_sens[grnum - 1](True) # master pan
            iter = store.iter_next(iter)       

    def delete(self, args):
        oscopy.Figure.delete(self, args)
        store = self.cbx_store
        iter = store.get_iter_first()
        iter = store.iter_next(iter)  # First item always sensitive
        while iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if grnum > len(self.graphs):
                store.set_value(iter, IOSCOPY_COL_VIS, False)
                self.mpsel_set_sens[grnum - 1](False) # master pan
                if grnum > 1 and self.mpsel_get_act[grnum - 1]():
                    self.mpsel_set_act[grnum - 2](True)
            else:
                store.set_value(iter, IOSCOPY_COL_VIS, True)
                self.mpsel_set_sens[grnum - 1](True) # master pan
            iter = store.iter_next(iter)       

    def button_press(self, event):
        if event.button == 3:
            print("Button 3...")
            return
            menu = self._create_figure_popup_menu(event.canvas.figure, event.inaxes)
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.guiEvent.time)

    def mouse_scroll(self, event):
        print(event.button)
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

    def axes_enter(self, event):
#        self._figure_enter(event)
#        self._current_graph = event.inaxes

#        axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
#        fig_num = self._ctxt.figures.index(self._current_figure) + 1
#        self._app_exec('%%oselect %d-%d' % (fig_num, axes_num))
        pass

    def axes_leave(self, event):
        # Unused for better user interaction
#        self._current_graph = None
        pass

    def figure_enter(self, event):
#        self._current_figure = event.canvas.figure
#        if hasattr(event, 'inaxes') and event.inaxes is not None:
#            axes_num = event.canvas.figure.axes.index(event.inaxes) + 1
#        else:
#            axes_num = 1
#        fig_num = self._ctxt.figures.index(self._current_figure) + 1
#        self._app_exec('%%oselect %d-%d' % (fig_num, axes_num))
        self.canvas.grab_focus()
        pass

    def figure_leave(self, event):
#        self._current_figure = None
        pass

    def show_coords(self, event):
        a = event.inaxes
        if a is not None:
            x = '%.3f %s%s' % (event.xdata,
                             oscopy.factors_to_names[a.scale_factors[0]][0],
                             a.unit[0] if a.unit[0] is not None else 'a.u.')
            y = '%.3f %s%s' % (event.ydata,
                             oscopy.factors_to_names[a.scale_factors[1]][0],
                             a.unit[1] if a.unit[1] is not None else 'a.u.')
            self.coords_lbl1.set_text(x)
            self.coords_lbl2.set_text(y)
        else:
            self.coords_lbl1.set_text('')
            self.coords_lbl2.set_text('')
            

    def _create_figure_popup_menu(self, figure, graph):
#        figmenu = gui.menus.FigureMenu()
#        return figmenu.create_menu(figure, graph)
        pass

    def update_scrollbars(self, unused):
        # Unused is not used but can be either a MPL event or a togglebutton
        (lower, upper) = (0, 1)
        (xpgs_min, ypgs_min) = (1, 1)
        (xvs, yvs) = ([], [])
        for grnum, gr in enumerate(self.graphs):
            (xv, xpgs, yv, ypgs) = self._update_graph_adj(grnum, gr)
            xpgs_min = min(xpgs_min, xpgs)
            ypgs_min = min(ypgs_min, ypgs)
            xvs.append(xv)
            yvs.append(yv)
        # Then for all graphs...
        for i, get_act in enumerate(self.mpsel_get_act):
            if get_act():
                break
        if xvs:
            hadj = self.cbx_store[0][IOSCOPY_COL_HADJ]
            hadj.configure(xvs[i], lower, upper,
                           xpgs_min / 10.0, xpgs_min, xpgs_min)
        if yvs:
            vadj = self.cbx_store[0][IOSCOPY_COL_VADJ]
            vadj.configure(-yvs[i], -upper, lower,
                            ypgs_min / 10.0, ypgs_min, ypgs_min)

    def _update_graph_adj(self, grnum, g):
        (lower, upper) = (0, 1)

        hadj = self.cbx_store[grnum + 1][IOSCOPY_COL_HADJ]
        vadj = self.cbx_store[grnum + 1][IOSCOPY_COL_VADJ]

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
        return (xvalue, xpage_size, yvalue, ypage_size)

    def hscroll_change_value(self, widget, scroll, value):
        (cbx, store) = (self.graphs_cbx, self.store)
        if self.layout == 'vert':
            return False
        iter = cbx.get_active_iter()
        layout = self.layout
        for mp, get_act in enumerate(self.mpsel_get_act):
            if get_act():
                break # Here is the master pan graph
        master_pan_gr = self.graphs[mp]
        if iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if store.get_string_from_iter(iter) == '0':
                # move only graphs having the same unit as selected master
                adj = widget.get_adjustment()
                val = adj.get_value()
                delta = (val - self.hadjpreval) if self.hadjpreval is not None else 0
                iter = store.iter_next(iter)
                while iter is not None:
                    grnum = int(store.get_string_from_iter(iter))
                    if grnum > len(self.graphs):
                        break
                    g = self.graphs[grnum - 1]
                    # Pan
                    if self.hadjpreval is None or g.get_unit()[0] != master_pan_gr.get_unit()[0]:
                        iter = store.iter_next(iter)
                        continue
                    hadj = self.cbx_store[grnum][IOSCOPY_COL_HADJ]
                    curval = hadj.get_value()
                    if ((val < curval and delta < 0) or (val > curval and delta > 0)) and val < 1 - hadj.get_page_size():
                        self._translate_to(g, val, None)
                        hadj.set_value(val) # Because the callback is disabled
                    iter = store.iter_next(iter)
                self.hadjpreval = widget.get_adjustment().get_value()
            else:
                g = self.graphs[grnum - 1]
                # Pan
                self._translate_to(g, widget.get_value(), None)
            self.canvas.draw_idle()
        return False

    def vscroll_change_value(self, widget, scroll, value):
        (cbx, store) = (self.graphs_cbx, self.store)
        if self.layout == 'horiz':
            return False
        iter = cbx.get_active_iter()
        layout = self.layout
        for mp, get_act in enumerate(self.mpsel_get_act):
            if get_act():
                break # Here is the master pan graph
        master_pan_gr = self.graphs[mp]
        if iter is not None:
            grnum = int(store.get_string_from_iter(iter))
            if store.get_string_from_iter(iter) == '0':
                # Move only graphs having the same unit as selected master
                adj = widget.get_adjustment()
                val = adj.get_value()
                delta = (val - self.vadjpreval) if self.vadjpreval is not None else 0
                iter = store.iter_next(iter)
                while iter is not None:
                    grnum = int(store.get_string_from_iter(iter))
                    if grnum > len(self.graphs):
                        break
                    g = self.graphs[grnum - 1]
                    # Pan
                    if self.vadjpreval is None or g.get_unit()[1] != master_pan_gr.get_unit()[1]:
                        iter = store.iter_next(iter)
                        continue
                    vadj = self.cbx_store[grnum][IOSCOPY_COL_VADJ]
                    curval = vadj.get_value()
                    if ((val < curval and delta < 0) or (val > curval and delta > 0)) and val < -vadj.get_page_size():
                        self._translate_to(g, None, val)
                        vadj.set_value(val) # Because the callback is disabled
                    iter = store.iter_next(iter)
                self.vadjpreval = widget.get_adjustment().get_value()
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
        if self.draw_hid is not None:
            self.canvas.mpl_disconnect(self.draw_hid)
            self.draw_hid = None

    def enable_adj_update_on_draw(self, widget, event):
        layout = self.layout
        if widget == self.hbar and layout not in ['horiz', 'quad']:
            return
        if widget == self.vbar and layout not in ['vert', 'quad']:
            return
        if self.draw_hid is None and not event.get_state() & Gdk.ModifierType.BUTTON1_MASK:
            self.draw_hid = self.canvas.mpl_connect('draw_event', self.update_scrollbars)

    def hadj_pressed(self, widget, event):
        self.hadjpreval = widget.get_value()

    def hadj_released(self, widget, event):
        self.hadjpreval = None

    def vadj_pressed(self, widget, event):
        self.vadjpreval = widget.get_value()

    def vadj_released(self, widget, event):
        self.vadjpreval = None

    layout = property(oscopy.Figure.get_layout, set_layout)

def error_msg_gtk(msg, parent=None):
    # From matplotlib/backends/backend_Gtk.py
    if parent is not None: # find the toplevel Gtk.Window
        parent = parent.get_toplevel()
        if parent.flags() & Gtk.TOPLEVEL == 0:
            parent = None

    if not is_string_like(msg):
        msg = ','.join(map(str,msg))

    dialog = Gtk.MessageDialog(
        parent         = parent,
        type           = Gtk.MessageType.ERROR,
        buttons        = Gtk.ButtonsType.OK,
        message_format = msg)
    dialog.run()
    dialog.destroy()
