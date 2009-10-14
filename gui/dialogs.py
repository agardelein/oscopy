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
        # Label and entry for X axis
        hbox_x = gtk.HBox()
        label_xunits = gtk.Label('X axis unit:')
        hbox_x.pack_start(label_xunits)
        self._entry_xunits = gtk.Entry()
        self._entry_xunits.set_text(units[0])
        hbox_x.pack_start(self._entry_xunits)
        self._dlg.vbox.pack_start(hbox_x)

        # Label and entry for Y axis
        hbox_y = gtk.HBox()
        label_yunits = gtk.Label('Y axis unit:')
        hbox_y.pack_start(label_yunits)
        self._entry_yunits = gtk.Entry()
        self._entry_yunits.set_text(units[1])
        hbox_y.pack_start(self._entry_yunits)
        self._dlg.vbox.pack_start(hbox_y)

        self._dlg.show_all()

    def run(self):
        units = ()
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            units = (self._entry_xunits.get_text(),\
                         self._entry_yunits.get_text())
        self._dlg.destroy()
        return units
