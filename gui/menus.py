import gtk

class FigureMenu(object):

    def FigureMenu(self):
        self._store = None

    def create_menu(self, store, figure, graph):
        self._layout_to_str = {'horiz': 'Horizontal', 'vert':'Vertical',\
                                   'quad':'Quad'}
        self._store = store
        menu = gtk.Menu()
        if graph is None:
            item_nograph = gtk.MenuItem('No graph selected')
            menu.append(item_nograph)
            return menu
        item_figure = gtk.MenuItem('Figure')
        item_figure.set_submenu(self._create_figure_menu(figure, graph))
        menu.append(item_figure)
        item_graph = gtk.MenuItem('Graph')
        item_graph.set_submenu(self._create_graph_menu(figure, graph))
        menu.append(item_graph)
        return menu

    def _create_figure_menu(self, fig, graph):
        menu = gtk.Menu()
        item_add = gtk.MenuItem('Add graph')
        item_add.connect('activate', self._graph_menu_item_activated,
                         (fig))
        menu.append(item_add)
        item_delete = gtk.MenuItem('Delete graph')
        item_delete.connect('activate', self._delete_graph_menu_item_activated,
                            (fig, graph))
        menu.append(item_delete)
        item_layout = gtk.MenuItem('Layout')
        item_layout.set_submenu(self._create_layout_menu(fig))
        menu.append(item_layout)
        return menu

    def _graph_menu_item_activated(self, menuitem, user_data):
        fig = user_data
        fig.add()
        fig.canvas.draw()

    def _delete_graph_menu_item_activated(self, menuitem, user_data):
        figure, graph = user_data
        if graph is not None:
            idx = figure.graphs.index(graph)
            figure.delete(idx + 1)
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

    def _create_graph_menu(self, figure, graph):
        graphmenu = GraphMenu()
        return graphmenu.create_graph_menu(self._store, figure, graph)

class GraphMenu(object):

    def GraphMenu(self):
        self._store = None
        pass

    def create_graph_menu(self, store, figure, graph):
        self._scale_to_str = {'lin': 'Linear', 'logx': 'LogX', 'logy': 'LogY',\
                                  'loglog': 'Loglog'}
        self._store = store
        menu = gtk.Menu()
        item_range = gtk.MenuItem('Range...')
        item_range.connect('activate', self._range_menu_item_activated,\
                               (figure, graph))
        menu.append(item_range)
        item_units = gtk.MenuItem('Units...')
        item_units.connect('activate', self._units_menu_item_activated,\
                               (figure, graph))
        menu.append(item_units)
        item_scale = gtk.MenuItem('Scale')
        item_scale.set_submenu(self._create_scale_menu((figure, graph)))
        menu.append(item_scale)
        item_add = gtk.MenuItem('Insert signal')
        item_add.set_submenu(self._create_filename_menu((figure, graph)))
        menu.append(item_add)
        item_remove = gtk.MenuItem('Remove signal')
        item_remove.set_submenu(self._create_remove_signal_menu((figure, graph)))
        menu.append(item_remove)
        return menu
    def _create_units_window(self, figure, graph):
        if graph is None:
            return
        dlg = gtk.Dialog('Enter graph units',\
                             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        # Label and entry for X axis
        hbox_x = gtk.HBox()
        label_xunits = gtk.Label('X axis unit:')
        hbox_x.pack_start(label_xunits)
        entry_xunits = gtk.Entry()
        entry_xunits.set_text(graph.unit[0])
        hbox_x.pack_start(entry_xunits)
        dlg.vbox.pack_start(hbox_x)

        # Label and entry for Y axis
        hbox_y = gtk.HBox()
        label_yunits = gtk.Label('Y axis unit:')
        hbox_y.pack_start(label_yunits)
        entry_yunits = gtk.Entry()
        entry_yunits.set_text(graph.unit[1])
        hbox_y.pack_start(entry_yunits)
        dlg.vbox.pack_start(hbox_y)

        dlg.show_all()
        resp = dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            graph.set_unit((entry_xunits.get_text(),\
                                             entry_yunits.get_text()))
            if figure.canvas is not None:
                figure.canvas.draw()
        dlg.destroy()

    def _units_menu_item_activated(self, menuitem, user_data):
        figure, graph = user_data
        self._create_units_window(figure, graph)

    def _create_range_window(self, figure, graph):
        if graph is None:
            return
        dlg = gtk.Dialog('Enter graph range',\
                             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        [xmin, xmax], [ymin, ymax] = graph.get_range()
        # Label and entry for X axis
        hbox_x = gtk.HBox()
        label_xmin = gtk.Label('Xmin:')
        hbox_x.pack_start(label_xmin)
        entry_xmin = gtk.Entry()
        entry_xmin.set_text(str(xmin))
        hbox_x.pack_start(entry_xmin)
        label_xmax = gtk.Label('Xmax:')
        hbox_x.pack_start(label_xmax)
        entry_xmax = gtk.Entry()
        entry_xmax.set_text(str(xmax))
        hbox_x.pack_start(entry_xmax)
        dlg.vbox.pack_start(hbox_x)

        # Label and entry for Y axis
        hbox_y = gtk.HBox()
        label_ymin = gtk.Label('Ymin:')
        hbox_y.pack_start(label_ymin)
        entry_ymin = gtk.Entry()
        entry_ymin.set_text(str(ymin))
        hbox_y.pack_start(entry_ymin)
        label_ymax = gtk.Label('Ymax:')
        hbox_y.pack_start(label_ymax)
        entry_ymax = gtk.Entry()
        entry_ymax.set_text(str(ymax))
        hbox_y.pack_start(entry_ymax)
        dlg.vbox.pack_start(hbox_y)

        dlg.show_all()
        resp = dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            r = [float(entry_xmin.get_text()),\
                     float(entry_xmax.get_text()),\
                     float(entry_ymin.get_text()),\
                     float(entry_ymax.get_text())]
            graph.set_range(r)
            if figure.canvas is not None:
                figure.canvas.draw()
        dlg.destroy()

    def _range_menu_item_activated(self, menuitem, user_data):
        figure, graph = user_data
        self._create_range_window(figure, graph)

    def _signals_menu_item_activated(self, menuitem, user_data):
        fig, graph, parent_it, it = user_data
        name, sig = self._store.get(it, 0, 1)
        # print 'Adding signal %s to %s' % (name, fig)
        if not fig.graphs:
            fig.add({name:sig})
        else:
            if graph is not None:
                graph.insert({name: sig})
        if fig.canvas is not None:
            fig.canvas.draw()

    def _scale_menu_item_activated(self, menuitem, user_data):
        figure, graph, scale = user_data
        graph.set_scale(scale)
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
            item_nograph = gtk.MenuItem('No graph selected')
            menu.append(item_nograph)
            return menu
        for name, signal in graph.signals.iteritems():
            item = gtk.MenuItem(name)
            item.connect('activate', self._remove_signal_menu_item_activated,
                         (figure, graph, {name: signal}))
            menu.append(item)
        return menu

    def _create_signals_menu(self, fig, graph, parent_it):
        menu = gtk.Menu()
        it = self._store.iter_children(parent_it)
        while it is not None:
            name = self._store.get_value(it, 0)
            item = gtk.MenuItem(name)
            item.connect('activate', self._signals_menu_item_activated,
                         (fig, graph, parent_it, it))
            menu.append(item)
            it = self._store.iter_next(it)
        return menu

    def _create_filename_menu(self, data):
        figure, graph = data
        it = self._store.get_iter_root()
        if it is None:
            return gtk.Menu()

        menu = gtk.Menu()
        while it is not None:
            filename = self._store.get_value(it, 0)
            item = gtk.MenuItem(filename)
            item.set_submenu(self._create_signals_menu(figure, graph, it))
            menu.append(item)
            it = self._store.iter_next(it)
        return menu

