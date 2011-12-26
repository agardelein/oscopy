import gtk
import dialogs
from oscopy.graphs import factors_to_names, abbrevs_to_factors

class FigureMenu(object):

    def __init__(self):
        pass

    def create_menu(self, figure, graph):
        self._layout_to_str = {'horiz': _('Horizontal'), 'vert':_('Vertical'),\
                                   'quad':_('Quad')}
        menu = gtk.Menu()
        self._create_figure_menu(menu, figure, graph)
        sep = gtk.SeparatorMenuItem()
        menu.append(sep)
        self._create_graph_menu(menu, figure, graph)

        return menu
    
    def _create_figure_menu(self, menu, fig, graph):
        item_add = gtk.MenuItem(_('Add graph'))
        item_add.connect('activate', self._add_graph_menu_item_activated,
                         (fig))
        menu.append(item_add)
        item_delete = gtk.MenuItem(_('Delete graph'))
        item_delete.connect('activate', self._delete_graph_menu_item_activated,
                            (fig, graph))
        item_delete.set_sensitive(graph is not None)
        menu.append(item_delete)
        item_layout = gtk.MenuItem(_('Layout'))
        item_layout.set_submenu(self._create_layout_menu(fig))
        menu.append(item_layout)
        return menu

    def _add_graph_menu_item_activated(self, menuitem, user_data):
        fig = user_data
        fig.add({})
        fig.canvas.draw()

    def _delete_graph_menu_item_activated(self, menuitem, user_data):
        figure, graph = user_data
        if graph is not None:
            idx = figure.graphs.index(graph) + 1
            figure.delete(idx)
            if figure.canvas is not None:
                figure.canvas.draw()

    def _create_layout_menu(self, fig):
        menu = gtk.Menu()
        for layout in self._layout_to_str.keys():
            item = gtk.CheckMenuItem(self._layout_to_str[layout])
            item.set_active(fig.layout == layout)
            item.connect('activate', self._layout_menu_item_activated,
                         (fig, layout))
            menu.append(item)
        return menu

    def _layout_menu_item_activated(self, menuitem, user_data):
        fig, layout = user_data
        fig.layout = layout
        if fig.canvas is not None:
            fig.canvas.draw()

    def _create_graph_menu(self, menu, figure, graph):
        graphmenu = GraphMenu()
        return graphmenu.create_graph_menu(menu, figure, graph)

class GraphMenu(object):

    def __init__(self):
        pass

    def create_graph_menu(self, menu, figure, graph):
        self._scale_to_str = {'lin': _('Linear'), 'logx': _('LogX'), 'logy': _('LogY'),\
                                  'loglog': _('Loglog')}
#        menu = gtk.Menu()
        item_range = gtk.MenuItem(_('Range...'))
        item_range.connect('activate', self._range_menu_item_activated,
                           (figure, graph))
        item_range.set_sensitive(graph is not None)
        menu.append(item_range)
        item_units = gtk.MenuItem(_('Units...'))
        item_units.connect('activate', self._units_menu_item_activated,
                           (figure, graph))
        item_units.set_sensitive(graph is not None)
        menu.append(item_units)
        item_scale = gtk.MenuItem(_('Scale'))
        item_scale.set_submenu(self._create_scale_menu((figure, graph)))
        item_scale.set_sensitive(graph is not None)
        menu.append(item_scale)
        item_remove = gtk.MenuItem(_('Remove signal'))
        item_remove.set_submenu(self._create_remove_signal_menu((figure, graph)))
        item_remove.set_sensitive(graph is not None)
        menu.append(item_remove)
        return menu

    def _create_units_window(self, figure, graph):
        if graph is None:
            return
        unitdlg = dialogs.Enter_Units_Dialog()
        unitdlg.display(graph.unit, graph.axis_names, graph.scale_factors)
        units, scale_factors = unitdlg.run()
        if units and scale_factors:
            graph.unit = units
            factors = (abbrev_to_factors[x] for x in scale_factors)
            graph.set_scale_factors(abbrevs_to_factors[scale_factors[0]],
                                    abbrevs_to_factors[scale_factors[1]])
            if figure.canvas is not None:
                figure.canvas.draw()

    def _units_menu_item_activated(self, menuitem, user_data):
        figure, graph = user_data
        self._create_units_window(figure, graph)

    def _create_range_window(self, figure, graph):
        if graph is None:
            return
        rangedlg = dialogs.Enter_Range_Dialog()
        rangedlg.display(graph.get_range(), graph.axis_names,
                         graph.scale_factors, graph.unit)
        r = rangedlg.run()
        if r:
            graph.range = [float(x) for x in r]
            if figure.canvas is not None:
                figure.canvas.draw()

    def _range_menu_item_activated(self, menuitem, user_data):
        figure, graph = user_data
        self._create_range_window(figure, graph)

    def _scale_menu_item_activated(self, menuitem, user_data):
        figure, graph, scale = user_data
        if graph is None:
            return
        graph.scale = scale
        if figure.canvas is not None:
            figure.canvas.draw()

    def _remove_signal_menu_item_activated(self, menuitem, user_data):
        figure, graph, signals = user_data
        if graph is None:
            return
        graph.remove(signals)
        if figure.canvas is not None:
            figure.canvas.draw()

    def _create_scale_menu(self, data):
        figure, graph = data
        if graph is None:
            return
        menu = gtk.Menu()
        for scale in self._scale_to_str.keys():
            item = gtk.CheckMenuItem(self._scale_to_str[scale])
            item.set_active(graph.scale == scale)
            item.connect('activate', self._scale_menu_item_activated,
                         (figure, graph, scale))
            menu.append(item)
        return menu

    def _create_remove_signal_menu(self, data):
        figure, graph = data
        menu = gtk.Menu()
        if graph is None:
            item_nograph = gtk.MenuItem(_('No graph selected'))
            menu.append(item_nograph)
            return menu
        for name, signal in graph.signals.iteritems():
            item = gtk.MenuItem(name)
            item.connect('activate', self._remove_signal_menu_item_activated,
                         (figure, graph, {name: signal}))
            menu.append(item)
        return menu

class TreeviewMenu:
        # item_add = gtk.MenuItem(_('Insert signal'))
        # item_add.set_submenu(self._create_filename_menu((figure, graph,
        #                                                  app_exec)))
        # item_add.set_sensitive(graph is not None)
        # menu.append(item_add)

    def _signals_menu_item_activated(self, menuitem, user_data):
        fig, graph, parent_it, it, app_exec = user_data
        name, sig = self._store.get(it, 0, 1)
        if not fig.graphs:
            app_exec('oadd %s' % name)
        else:
            if graph is not None:
                app_exec('oinsert %s' % name)
        if fig.canvas is not None:
            fig.canvas.draw()

    def _create_signals_menu(self, fig, graph, parent_it, app_exec):
        menu = gtk.Menu()
        it = self._store.iter_children(parent_it)
        while it is not None:
            name = self._store.get_value(it, 0)
            item = gtk.MenuItem(name)
            item.connect('activate', self._signals_menu_item_activated,
                         (fig, graph, parent_it, it, app_exec))
            menu.append(item)
            it = self._store.iter_next(it)
        return menu

    def _create_filename_menu(self, data):
        figure, graph, app_exec = data
        it = self._store.get_iter_root()
        if it is None:
            return gtk.Menu()

        menu = gtk.Menu()
        while it is not None:
            filename = self._store.get_value(it, 0)
            item = gtk.MenuItem(filename)
            item.set_submenu(self._create_signals_menu(figure, graph, it,
                                                       app_exec))
            menu.append(item)
            it = self._store.iter_next(it)
        return menu

