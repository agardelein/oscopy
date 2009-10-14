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

class Enter_Range_Dialog(object):
    def Enter_Range_Dialog(self):
        pass

    def display(self, r):
        self._dlg = gtk.Dialog('Enter graph range',\
                             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        [xmin, xmax], [ymin, ymax] = r
        # Label and entry for X axis
        hbox_x = gtk.HBox()
        label_xmin = gtk.Label('Xmin:')
        hbox_x.pack_start(label_xmin)
        self._entry_xmin = gtk.Entry()
        self._entry_xmin.set_text(str(xmin))
        hbox_x.pack_start(self._entry_xmin)
        label_xmax = gtk.Label('Xmax:')
        hbox_x.pack_start(label_xmax)
        self._entry_xmax = gtk.Entry()
        self._entry_xmax.set_text(str(xmax))
        hbox_x.pack_start(self._entry_xmax)
        self._dlg.vbox.pack_start(hbox_x)

        # Label and entry for Y axis
        hbox_y = gtk.HBox()
        label_ymin = gtk.Label('Ymin:')
        hbox_y.pack_start(label_ymin)
        self._entry_ymin = gtk.Entry()
        self._entry_ymin.set_text(str(ymin))
        hbox_y.pack_start(self._entry_ymin)
        label_ymax = gtk.Label('Ymax:')
        hbox_y.pack_start(label_ymax)
        self._entry_ymax = gtk.Entry()
        self._entry_ymax.set_text(str(ymax))
        hbox_y.pack_start(self._entry_ymax)
        self._dlg.vbox.pack_start(hbox_y)

        self._dlg.show_all()

    def run(self):
        r = []
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            r = [float(self._entry_xmin.get_text()),\
                     float(self._entry_xmax.get_text()),\
                     float(self._entry_ymin.get_text()),\
                     float(self._entry_ymax.get_text())]
        self._dlg.destroy()
        return r
