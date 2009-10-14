import gtk

class Enter_Units_Dialog(object):
    def Enter_Units_Dialog(self):
        self._dlg = None
        self._entry_xunits = None
        self._entry_yunits = None
        pass

    def display(self, units):
        self._dlg = gtk.Dialog('Enter graph units',\
                                  buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                               gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        table = gtk.Table(2, 2, False)
        table.set_col_spacing(0, 12)
        table.set_col_spacing(1, 12)
        # Label and entry for X axis
        label_xunits = gtk.Label('X axis unit:')
        table.attach(label_xunits, 0, 1, 0, 1)
        self._entry_xunits = gtk.Entry()
        self._entry_xunits.set_text(units[0])
        table.attach(self._entry_xunits, 1, 2, 0, 1)

        # Label and entry for Y axis
        label_yunits = gtk.Label('Y axis unit:')
        table.attach(label_yunits, 0, 1, 1, 2)
        self._entry_yunits = gtk.Entry()
        self._entry_yunits.set_text(units[1])
        table.attach(self._entry_yunits, 1, 2, 1, 2)
        self._dlg.vbox.pack_start(table)
        self._dlg.set_border_width(12)

        self._dlg.show_all()

    def run(self):
        units = ()
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            units = (self._entry_xunits.get_text(),\
                         self._entry_yunits.get_text())
        self._dlg.destroy()
        return units
