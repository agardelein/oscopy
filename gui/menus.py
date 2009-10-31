import gtk
import dialogs

class FigureMenu(object):

    def __init__(self):
        self._store = None

    def create_menu(self, store, figure, graph, app_exec):
        self._layout_to_str = {'horiz': 'Horizontal', 'vert':'Vertical',\
                                   'quad':'Quad'}
        self._store = store
        menu = gtk.Menu()
        if graph is None:
            item_nograph = gtk.MenuItem('No graph selected')
            menu.append(item_nograph)
            return menu
        item_figure = gtk.MenuItem('Figure')
        item_figure.set_submenu(self._create_figure_menu(figure, graph, app_exec))
        menu.append(item_figure)
        item_graph = gtk.MenuItem('Graph')
        item_graph.set_submenu(self._create_graph_menu(figure, graph, app_exec))
        menu.append(item_graph)
        return menu

    def _create_figure_menu(self, fig, graph, app_exec):
        menu = gtk.Menu()
        item_add = gtk.MenuItem('Add graph')
        item_add.connect('activate', self._graph_menu_item_activated,
                         (fig, app_exec))
        menu.append(item_add)
        item_delete = gtk.MenuItem('Delete graph')
        item_delete.connect('activate', self._delete_graph_menu_item_activated,
                            (fig, graph, app_exec))
        menu.append(item_delete)
        item_layout = gtk.MenuItem('Layout')
        item_layout.set_submenu(self._create_layout_menu(fig, app_exec))
        menu.append(item_layout)
        return menu

    def _graph_menu_item_activated(self, menuitem, user_data):
        fig, app_exec = user_data
        app_exec('add')
        fig.canvas.draw()

    def _delete_graph_menu_item_activated(self, menuitem, user_data):
        figure, graph, app_exec = user_data
        if graph is not None:
            idx = figure.graphs.index(graph) + 1
            app_exec('delete %d' % idx)
            if figure.canvas is not None:
                figure.canvas.draw()

    def _create_layout_menu(self, fig, app_exec):
        menu = gtk.Menu()
        for layout in self._layout_to_str.keys():
            item = gtk.CheckMenuItem(self._layout_to_str[layout])
            item.set_active(fig.layout == layout)
            item.connect('activate', self._layout_menu_item_activated,
                         (fig, layout, app_exec))
            menu.append(item)
        return menu

    def _layout_menu_item_activated(self, menuitem, user_data):
        fig, layout, app_exec = user_data
        app_exec('layout ' + layout)
        if fig.canvas is not None:
            fig.canvas.draw()

    def _create_graph_menu(self, figure, graph, app_exec):
        graphmenu = GraphMenu()
        return graphmenu.create_graph_menu(self._store, figure, graph, app_exec)

class GraphMenu(object):

    def __init__(self):
        self._store = None
        pass

    def create_graph_menu(self, store, figure, graph, app_exec):
        self._scale_to_str = {'lin': 'Linear', 'logx': 'LogX', 'logy': 'LogY',\
                                  'loglog': 'Loglog'}
        self._store = store
        menu = gtk.Menu()
        item_range = gtk.MenuItem('Range...')
        item_range.connect('activate', self._range_menu_item_activated,
                           (figure, graph, app_exec))
        menu.append(item_range)
        item_units = gtk.MenuItem('Units...')
        item_units.connect('activate', self._units_menu_item_activated,
                           (figure, graph, app_exec))
        menu.append(item_units)
        item_scale = gtk.MenuItem('Scale')
        item_scale.set_submenu(self._create_scale_menu((figure, graph,
                                                        app_exec)))
        menu.append(item_scale)
        item_add = gtk.MenuItem('Insert signal')
        item_add.set_submenu(self._create_filename_menu((figure, graph,
                                                         app_exec)))
        menu.append(item_add)
        item_remove = gtk.MenuItem('Remove signal')
        item_remove.set_submenu(self._create_remove_signal_menu((figure, graph,
                                                                 app_exec)))
        menu.append(item_remove)
        return menu

    def _create_units_window(self, figure, graph, app_exec):
        if graph is None:
            return
        unitdlg = dialogs.Enter_Units_Dialog()
        unitdlg.display(graph.unit)
        units = unitdlg.run()
        if units:
            app_exec('unit %s' % ' '.join(units))
            if figure.canvas is not None:
                figure.canvas.draw()


    def _units_menu_item_activated(self, menuitem, user_data):
        figure, graph, app_exec = user_data
        self._create_units_window(figure, graph, app_exec)

    def _create_range_window(self, figure, graph, app_exec):
        if graph is None:
            return
        rangedlg = dialogs.Enter_Range_Dialog()
        rangedlg.display(graph.get_range())
        r = rangedlg.run()
        if r:
            app_exec('range %s' % ' '.join(r))
            if figure.canvas is not None:
                figure.canvas.draw()

    def _range_menu_item_activated(self, menuitem, user_data):
        figure, graph, app_exec = user_data
        self._create_range_window(figure, graph, app_exec)

    def _signals_menu_item_activated(self, menuitem, user_data):
        fig, graph, parent_it, it, app_exec = user_data
        name, sig = self._store.get(it, 0, 1)
        if not fig.graphs:
            app_exec('add %s' % name)
        else:
            if graph is not None:
                app_exec('insert %s' % name)
        if fig.canvas is not None:
            fig.canvas.draw()

    def _scale_menu_item_activated(self, menuitem, user_data):
        figure, graph, scale, app_exec = user_data
        app_exec('scale %s' % scale)
        if figure.canvas is not None:
            figure.canvas.draw()

    def _remove_signal_menu_item_activated(self, menuitem, user_data):
        figure, graph, signals, app_exec = user_data
        if graph is None:
            return
        app_exec('remove %s' % ' '.join(signals.keys()))
        if figure.canvas is not None:
            figure.canvas.draw()

    def _create_scale_menu(self, data):
        figure, graph, app_exec = data
        menu = gtk.Menu()
        for scale in self._scale_to_str.keys():
            item = gtk.CheckMenuItem(self._scale_to_str[scale])
            item.set_active(graph.scale == scale)
            item.connect('activate', self._scale_menu_item_activated,
                         (figure, graph, scale, app_exec))
            menu.append(item)
        return menu

    def _create_remove_signal_menu(self, data):
        figure, graph, app_exec = data
        menu = gtk.Menu()
        if graph is None:
            item_nograph = gtk.MenuItem('No graph selected')
            menu.append(item_nograph)
            return menu
        for name, signal in graph.signals.iteritems():
            item = gtk.MenuItem(name)
            item.connect('activate', self._remove_signal_menu_item_activated,
                         (figure, graph, {name: signal}, app_exec))
            menu.append(item)
        return menu

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

