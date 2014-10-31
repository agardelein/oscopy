from gi.repository import Gtk, Gio, Gdk, GLib, GObject
from gi.repository import Pango, PangoCairo
import cairo
from .gtk_figure import IOscopy_GTK_Figure
import oscopy

IOSCOPY_SIGNAL_LIST_UI = 'oscopy/signal-list.ui'

class OscopyTreeViewDetails(GObject.GObject):
    """ From struct NautilusListViewDetails
    https://git.gnome.org/browse/nautilus/tree/src/nautilus-list-view.c
    """

    def __init__(self):
        self.tree_view = None
        self.model = None
        self.list_action_group = None
        self.list_merge_id = None
        self.signal_name_column = None
        self.signal_name_column_num = 0
        self.pixbul_cell = None
        self.signal_name_cell = None
        self.cells = None
        self.editable_widget = None
        self.drag_dest = None
        self.double_click_path = [None, None]
        self.new_selection_path = None
        self.hover_path = None
        self.drag_button = 0
        self.drag_x = 0
        self.drag_y = 0
        self.drag_started = False
        self.ignore_button_release = False
        self.row_selected_on_button_down = False
        self.menus_ready = False
        self.active = False
        self.columns = None
        self.column_editor = None
        self.clipboard_handler_id = 0

class IOscopyAppWin(Gtk.ApplicationWindow):
    TARGET_TYPE_SIGNAL = 10354
    def __init__(self, app, uidir=None):
        Gtk.ApplicationWindow.__init__(self, title='IOscopy', application=app)
        self.app = app
        self.popup = None

        self.from_signal_list = [Gtk.TargetEntry.new("text/plain",
                                                      Gtk.TargetFlags.SAME_APP,
                                                      self.TARGET_TYPE_SIGNAL)]

        self.to_main_win = [Gtk.TargetEntry.new("text/plain", 0,
                                                self.TARGET_TYPE_SIGNAL),
                            Gtk.TargetEntry.new('STRING', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            Gtk.TargetEntry.new('application/octet-stream', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            # For '*.raw' formats
                            Gtk.TargetEntry.new('application/x-panasonic-raw', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            # For '*.ts' formats
                            Gtk.TargetEntry.new('video/mp2t', 0,
                                                self.TARGET_TYPE_SIGNAL),
                            ]

        # For multiple drag and drop with TreeView
        self.rows_for_drag = []
        self.last_click_time = 0
        self.details = OscopyTreeViewDetails()

        # The remaining widgets
        self.builder = Gtk.Builder()
        self.builder.expose_object('store', self.app.store)
        self.builder.add_from_file('/'.join((self.app.uidir, IOSCOPY_SIGNAL_LIST_UI)))
        self.add(self.builder.get_object('scwin'))
        self.set_default_size(400, 300)
        handlers = {'row_activated': self.row_activated,
                    'drag_data_get': self.drag_data_get,
                    'tv_button_pressed': self.treeview_button_press,
                    'cell_toggled': self.cell_toggled,
                    'tv_button_released': self.treeview_button_release,
                    'tv_motion_notify_event': self.treeview_motion_notify,
                    }
        self.builder.connect_signals(handlers)

        # Bold font for file names
        col = self.builder.get_object('tvc')
        col.set_cell_data_func(self.builder.get_object('tvcrt'), self.reader_name_in_bold)        
        # Drag setup
        tv = self.builder.get_object('tv')
        tv.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                        self.from_signal_list,
                                        Gdk.DragAction.COPY)
        tv.get_selection().connect('changed', self.tv_selection_changed)
        tv.get_selection().set_select_function(self.tv_sel_select)
        tv.connect_after('drag-begin', self.drag_begin)
        self.details.tree_view = tv

        # Drop setup
        self.drag_dest_set(Gtk.DestDefaults.MOTION |\
                        Gtk.DestDefaults.HIGHLIGHT |\
                        Gtk.DestDefaults.DROP,
                        self.to_main_win, Gdk.DragAction.COPY)
        self.connect('drag_data_received', self.drag_data_received)

        # Just hide, don't destroy window
        self.connect('destroy', lambda w, e: w.hide() or True)
        self.connect('delete-event', lambda w, e: w.hide() or True)

    def reader_name_in_bold(self, column, cell, model, iter, data=None):
        if len(model.get_path(iter)) == 1:
            cell.set_property('markup', "<b>" + model.get_value(iter, 0) +\
                                  "</b>")
        else:
            cell.set_property('text', model.get_value(iter, 0))

    def row_activated(self, widget, path, col):
        if len(path) == 1:
            return

        row = self.app.store[path]
        self.app.exec_str('ocreate %s' % row[0])


    def tv_sel_select(selection, model, path, path_currently_selected,
                      data=None):
        if path_currently_selected.get_depth() > 1:
            return True
        else:
            return False

    def treeview_button_press(self, widget, event):
        # Based on Nautilus button-press-event callback
        # https://git.gnome.org/browse/nautilus/tree/src/nautilus-list-view.c
        #
        click_count = 0

        tv = widget
        sel = tv.get_selection()
        on_expander = False
        # Don't handle extra mouse button here
        if event.button > 5:
            return False

        if event.window != tv.get_bin_window():
            return False

        # Not implementing nautilus_list_model_set_drag_view call
        double_click_time = tv.get_settings().get_default().get_property('gtk-double-click-time')

        # Determine click count
        current_time = GLib.get_monotonic_time()
        if current_time - self.last_click_time < double_click_time:
            click_count = click_count + 1
        else:
            click_count = 0

        # Stash time for next compare
        self.last_click_time = current_time
        # Not implementing nautilus single click mode

        self.details.ignore_button_release = False
        is_simple_click = ((event.button == 1 or event.button == 2) and (event.type == Gdk.EventType.BUTTON_PRESS))
        ret = tv.get_path_at_pos(event.x, event.y)
        if ret is None:
            if is_simple_click:
                self.details.double_click_path[1] = self.details.double_click_path[0]
                self.details.double_click_path[0] = None
            # Deselect if people click outside any row. It's OK to let default
            # code run; it won't reselect anything.
            sel.unselect_all()
            tv.do_button_press_event(tv, event)

            if event.button == 3:
                return self.make_menu(event)
        
            return True

        (path, column, cell_x, cell_y) = ret

        call_parent = True
        path_selected = sel.path_is_selected(path)
        
        # Manage expander stuff
        expander_size = tv.style_get_property('expander-size')
        horizontal_separator = tv.style_get_property('horizontal-separator')
        # TODO we should not hardcode this extra padding. It is
        # EXPANDER_EXTRA_PADDING from GtkTreeView
        expander_size += 4
        on_expander = (event.x <= horizontal_separator / 2 +
                       path.get_depth() * expander_size)

        # Keep track of last click so double click only happen on the same item
        if is_simple_click:
            self.details.double_click_path[1] = self.details.double_click_path[0]
            self.details.double_click_path[0] = path.copy()
            
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            # Double clicking does not trigger a DnD action
            self.details.drag_button = 0

            if not on_expander and \
               self.details.double_click_path[1] and not \
               self.details.double_click_path[1].compare(self.details.double_click_path[0]):
                # Activate the cells on button 1 double-click
                tv.row_activated(path, column)
            else:
                tv.do_button_press_event(tv, event)
        else:
            # We're going to filter out some situations where we can't let
            # the default code run because all but one row would be deselected.
            # We don't want that; we want the right click menu or single click
            # to apply to everything that's currently selected.

            if event.button == 3 and path_selected:
                call_parent = False

            if (event.button == 1 or event.button == 2) and \
               ((event.state & Gdk.ModifierType.CONTROL_MASK) or not\
                (event.state & Gdk.ModifierType.SHIFT_MASK)):
                self.details.row_selected_on_button_down = path_selected
                if path_selected:
                    call_parent = on_expander
                    self.details.ignore_button_release = on_expander
                    if event.state & Gdk.ModifierType.CONTROL_MASK:
                        sel.unselect_path(path)

                elif event.state & Gdk.ModifierType.CONTROL_MASK:
                    selected_rows = None
                    l = None

                    call_parent = False
                    if event.state & Gdk.ModifierType.SHIFT_MASK:
                        cursor = None
                        (cursor, fc) = tv.get_cursor()
                        if cursor is not None:
                            sel.select_range(cursor, path)
                        else:
                            sel.select_path(path)
                    else:
                        sel.select_path(path)
                    selected_rows = sel.get_selected_rows()[1]
                    
                    # This unselects everything
                    tv.set_cursor(path, None, False)

                    # So select it again
                    for p in selected_rows:
                        sel.select_path(p)
                else:
                    self.details.ignore_button_release = on_expander

            if call_parent:
                tv.handler_block_by_func(self.row_activated)
                tv.do_button_press_event(tv, event)
                tv.handler_unblock_by_func(self.row_activated)
            elif path_selected:
                tv.grab_focus()

            if is_simple_click and not on_expander:
                self.details.drag_started = False
                self.details.drag_button = event.button
                self.details.drag_x = event.x
                self.details.drag_y = event.y

            if event.button == 3:
                # Popup menu
                return self.make_menu(event)

        return True

    def treeview_button_release(self, widget, event):
        if event.button == self.details.drag_button:
            self.stop_drag_check()
            if not self.details.drag_started and not self.details.ignore_button_release:
                self.treeview_did_not_drag(event)
        return False

    def stop_drag_check(self):
        self.details.drag_button = 0

    def treeview_did_not_drag(self, event):
        tv = self.details.tree_view
        sel = tv.get_selection()
        
        ret = tv.get_path_at_pos(event.x, event.y)
        if ret is None:
            return
        
        (path, column, cell_x, cell_y) = ret
        if (event.button == 1 or event.button == 2) and \
               ((event.state & Gdk.ModifierType.CONTROL_MASK) or not\
                (event.state & Gdk.ModifierType.SHIFT_MASK)) and \
               self.details.row_selected_on_button_down:
            if not self.button_event_modifies_selection(event):
                sel.unselect_all()
                sel.select_path(path)
            else:
                sel.unselect_path(path)
        
    def button_event_modifies_selection(self, event):
        return event.state & (Gdk.ModifierType.CONTROL_MASK | \
                               Gdk.ModifierType.SHIFT_MASK) != 0

    def treeview_motion_notify(self, widget, event):
        tv = widget
        if event.window != tv.get_bin_window():
            return False

        # Not implementing Nautilus click policy single stuff

        if self.details.drag_button:
            # Not implementing source_target_list stuff
            source_target_list = tv.drag_source_get_target_list()
            # since contained in self.from_list
            if tv.drag_check_threshold(self.details.drag_x, self.details.drag_y, event.x, event.y):
                tv.drag_begin_with_coordinates(source_target_list,
                                               Gdk.DragAction.MOVE | \
                                               Gdk.DragAction.COPY | \
                                               Gdk.DragAction.LINK | \
                                               Gdk.DragAction.ASK,
                                               self.details.drag_button,
                                               event,
                                               event.x,
                                               event.y)
            return True
        return False

    def get_drag_surface(self):
        tv = self.details.tree_view
        sel = tv.get_selection()
        model = tv.get_model()
        names = []
        # FIXME: Hardcoded padding
        PADDING = 4
        MAX_NAMES = 7

        # Get the names
        for path in sel.get_selected_rows()[1]:
            iter = model.get_iter(path)
            names.append(model.get_value(iter, 0))

        # Prepare the layout with only firsts MAX_NAMES
        layout = tv.create_pango_layout('\n'.join(names[0:MAX_NAMES]))
        (width, height) = layout.get_size()

        w = int(width/Pango.SCALE + PADDING * 2.0)
        h = int(height/Pango.SCALE + PADDING * 2.0)

        # Prepare the surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        cr = cairo.Context(surface)
        cr.rectangle (0, 0, w, h)
        cr.set_source_rgb (0.0, 0.0, 0.0)

        # Place the layout on the surface
        PangoCairo.update_layout(cr, layout)
        cr.move_to(PADDING, PADDING)
        PangoCairo.show_layout(cr, layout)

        # Make it transparent with a linear gradient
        gradient_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        cr = cairo.Context(gradient_surface)
        pat = cairo.LinearGradient(0.0, 0.0, 0.0, h)
        pat.add_color_stop_rgba(1, 1.0, 1.0, 1.0, 0.0)
        pat.add_color_stop_rgba(0, 0.0, 0.0, 0.0, 1.0)
        cr.set_source_surface(surface, 0, 0)
        cr.rectangle(0, 0, w, h)
        cr.mask(pat)

        return gradient_surface

    def drag_begin(self, widget, context):
        surface = self.get_drag_surface()

        if surface :
            surface.set_device_offset(0, 0)
            self.surface = surface
            Gtk.drag_set_icon_surface(context, surface)
        else:
            Gtk.drag_set_icon_default(context)

        self.stop_drag_check()
        
        # TODO : implement selection cache ?
        selection_cache = self.drag_create_selection_cache()
        # context.drag_info = selection_cache

    def drag_create_selection_cache(self):
        # TODO : implement selection cache ?
        return False

    def tv_selection_changed(self, widget):
        # Store the selection for drag and drop
        self.rows_for_drag = widget.get_selected_rows()[1]

    def cell_toggled(self, cellrenderer, path):
        if len(path) == 3:
            # Single signal
            if self.app.store[path][1].freeze:
                cmd = 'ounfreeze'
            else:
                cmd = 'ofreeze'
            self.app.exec_str('%s %s' % (cmd, self.app.store[path][0]))
        elif len(path) == 1:
            # Whole reader
            parent = self.app.store.get_iter(path)
            freeze = not self.app.store.get_value(parent, 2)
            if self.app.store[path][2]:
                cmd = 'ounfreeze'
            else:
                cmd = 'ofreeze'
            self.app.store.set_value(parent, 2, freeze)
            iter = self.app.store.iter_children(parent)
            while iter:
                self.app.exec_str('%s %s' % (cmd, self.app.store.get_value(iter, 0)))
                iter = self.app.store.iter_next(iter)

    def drag_data_get(self, widget, drag_context, data, target_type,\
                              time):
        if target_type == self.TARGET_TYPE_SIGNAL:
            tv = widget
            sel = tv.get_selection()
            (model, pathlist) = sel.get_selected_rows()
            iter = self.app.store.get_iter(pathlist[0])
            # Use the path list stored while button 1 has been pressed
            # See self._treeview_button_press()
            siglist = ' '.join([self.app.store[x][1].name for x in self.rows_for_drag])
            data.set_text(siglist, -1)
            return True

    def drag_data_received(self, widget, drag_context, x, y, data,
                           target_type, time):
        name = data.get_text()
        if type(name) == str and name.startswith('file://'):
            self.app.exec_str('%%oread %s' % name[7:].strip())

    def make_menu(self, event):
        menu_model = Gio.Menu.new()
        
        menu_model.append_submenu('Insert...', self.make_figures_submenu())
        menu = Gtk.Menu.new_from_model(menu_model)
        menu.attach_to_widget(self, None)
        menu.popup(None, None, None, None, event.button, event.time)
        return True

    def make_figures_submenu(self):
        tv = self.details.tree_view
        sel = tv.get_selection()
        model = tv.get_model()
        names = []
        # Get the names
        for path in sel.get_selected_rows()[1]:
            iter = model.get_iter(path)
            names.append(model.get_value(iter, 0))     

        menu = Gio.Menu.new()
        item = Gio.MenuItem.new('In new figure', 'app.insert_signal')
        param = GLib.Variant.new_tuple(GLib.Variant.new_string(','.join(names)),
                                           GLib.Variant.new_string(''),
                                           GLib.Variant.new_uint64(0))
        item.set_action_and_target_value('app.insert_signal', param)
        menu.append_item(item)
        for i, figure in enumerate(self.app.ctxt.figures):
            menu.append_submenu('Figure %d' % (i + 1), self.make_graphs_submenu_for_figure(figure, i, names))
        return menu

    def make_graphs_submenu_for_figure(self, figure, fignum, names):
        menu = Gio.Menu.new()
        if len(figure.graphs) < oscopy.MAX_GRAPHS_PER_FIGURE:
            item = Gio.MenuItem.new('In new graph', 'app.insert_signal')
            param = GLib.Variant.new_tuple(GLib.Variant.new_string(','.join(names)),
                                           GLib.Variant.new_string('Figure %d' % (fignum + 1)),
                                           GLib.Variant.new_uint64(0))
            item.set_action_and_target_value('app.insert_signal', param)
            menu.append_item(item)
        for i, graph in enumerate(figure.graphs):
            item = Gio.MenuItem.new('Graph %d' % (i + 1), 'app.insert_signal')
            param = GLib.Variant.new_tuple(GLib.Variant.new_string(','.join(names)),
                                           GLib.Variant.new_string('Figure %d' % (fignum + 1)),
                                           GLib.Variant.new_uint64(i + 1))
            item.set_action_and_target_value('app.insert_signal', param)
            menu.append_item(item)
        return menu
