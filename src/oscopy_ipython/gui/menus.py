from gi.repository import Gtk
from . import dialogs
from oscopy.graphs import factors_to_names, abbrevs_to_factors
from oscopy import MAX_GRAPHS_PER_FIGURE

class FigureMenu(object):

    def __init__(self):
        pass

    def create_menu(self, figure, graph):
        self._layout_to_str = {'horiz': _('Horizontal'), 'vert':_('Vertical'),\
                                   'quad':_('Quad')}
        menu = Gtk.Menu()
        self._create_figure_menu(menu, figure, graph)
        sep = Gtk.SeparatorMenuItem()
        menu.append(sep)
        self._create_graph_menu(menu, figure, graph)

        return menu
    
    def _create_figure_menu(self, menu, fig, graph):
        item_add = Gtk.MenuItem(_('Add graph'))
        item_add.connect('activate', self._add_graph_menu_item_activated,
                         (fig))
        item_add.set_sensitive(len(fig.graphs) < MAX_GRAPHS_PER_FIGURE)
        menu.append(item_add)
        item_delete = Gtk.MenuItem(_('Delete graph'))
        item_delete.connect('activate', self._delete_graph_menu_item_activated,
                            (fig, graph))
        item_delete.set_sensitive(graph is not None)
        menu.append(item_delete)
        item_layout = Gtk.MenuItem(_('Layout'))
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
        menu = Gtk.Menu()
        for layout in list(self._layout_to_str.keys()):
            item = Gtk.CheckMenuItem(self._layout_to_str[layout])
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
#        menu = Gtk.Menu()
        item_range = Gtk.MenuItem(_('Range...'))
        item_range.connect('activate', self._range_menu_item_activated,
                           (figure, graph))
        item_range.set_sensitive(graph is not None)
        menu.append(item_range)
        item_units = Gtk.MenuItem(_('Units...'))
        item_units.connect('activate', self._units_menu_item_activated,
                           (figure, graph))
        item_units.set_sensitive(graph is not None)
        menu.append(item_units)
        item_scale = Gtk.MenuItem(_('Scale'))
        item_scale.set_submenu(self._create_scale_menu((figure, graph)))
        item_scale.set_sensitive(graph is not None)
        menu.append(item_scale)
        item_remove = Gtk.MenuItem(_('Remove signal'))
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
        menu = Gtk.Menu()
        for scale in list(self._scale_to_str.keys()):
            item = Gtk.CheckMenuItem(self._scale_to_str[scale])
            item.set_active(graph.scale == scale)
            item.connect('activate', self._scale_menu_item_activated,
                         (figure, graph, scale))
            menu.append(item)
        return menu

    def _create_remove_signal_menu(self, data):
        figure, graph = data
        menu = Gtk.Menu()
        if graph is None:
            item_nograph = Gtk.MenuItem(_('No graph selected'))
            menu.append(item_nograph)
            return menu
        for name, signal in graph.signals.items():
            item = Gtk.MenuItem(name)
            item.connect('activate', self._remove_signal_menu_item_activated,
                         (figure, graph, {name: signal}))
            menu.append(item)
        return menu

class TreeviewMenu:
    def __init__(self, create_func):
        self._signals = None
        self._create = create_func

    def make_menu(self, figures, signals):
        self._signals = signals
        menu = Gtk.Menu()
        item = Gtk.MenuItem(_('Insert Signal...'))
        item.set_submenu(self._make_figure_menu(figures))
        menu.append(item)
        return menu

    def _make_figure_menu(self, figures):
        menu = Gtk.Menu()
        for f in figures:
            item = Gtk.MenuItem(f.window.get_title())
            item.set_submenu(self._make_graph_menu(f))
            menu.append(item)
        item = Gtk.MenuItem(_('In new figure'))
        item.connect('activate', self._make_figure_menu_item_activated)
        menu.append(item)
        return menu

    def _make_graph_menu(self, figure):
        menu = Gtk.Menu()
        for i, g in enumerate(figure.graphs):
            name = _('Graph %d') % (i + 1)
            item = Gtk.MenuItem(name)
            item.connect('activate',
                         self._insert_signals_to_graph_menu_item_activated,
                         g, figure)
            menu.append(item)
        item = Gtk.MenuItem(_('In new graph'))
        item.connect('activate', self._add_graph_menu_item_activated, figure)
        item.set_sensitive(len(figure.graphs) < MAX_GRAPHS_PER_FIGURE)
        menu.append(item)
        return menu

    def _add_graph_menu_item_activated(self, menuitem, figure):
        figure.add(self._signals)
        figure.canvas.draw()

    def _make_figure_menu_item_activated(self, menuitem):
        self._create(self._signals)

    def _insert_signals_to_graph_menu_item_activated(self, menuitem, graph,
                                                     figure):
        graph.insert(self._signals)
        figure.canvas.draw()
