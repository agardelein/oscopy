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
        self._dlg = None
        self._entries = None

    def display(self, r):
        self._dlg = gtk.Dialog('Enter graph range',\
                             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                          gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        # Label and entry for X axis
        self._entries = []
        xy = ['X', 'Y']
        minmax = ['min', 'max']
        table = gtk.Table(2, 4, False)
        for col in range(0, 4):
            table.set_col_spacing(col, 12)
        for row in range(0, 2):
            entries_row = []
            for col in range(0, 4, 2):
                label = gtk.Label(xy[row] + minmax[col / 2])
                entry = gtk.Entry()
                entry.set_text(str(r[row][col/2]))
                table.attach(label, col, col + 1, row, row + 1)
                table.attach(entry, col + 1, col + 2, row, row + 1)
                entries_row.append(entry)
            self._entries.append(entries_row)
                
        self._dlg.vbox.pack_start(table)
        self._dlg.set_border_width(12)

        self._dlg.show_all()

    def run(self):
        r = []
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            r = [float(self._entries[0][0].get_text()),\
                     float(self._entries[0][1].get_text()),\
                     float(self._entries[1][0].get_text()),\
                     float(self._entries[1][1].get_text())]
        self._dlg.destroy()
        return r

class Run_Netlister_and_Simulate_Dialog:
    def Run_Netlister_and_Simulate_Dialog(self):
        self._dlg = None
        pass

    def display(self, actions):
        # Define functions to enable/disable entries upon toggle buttons
        # make window a bit larger
        self._dlg = gtk.Dialog("Run netlister and simulate",\
                                      buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,\
                                                   gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        vbox_netl = gtk.VBox()
        self._entry_netl = gtk.Entry()
        self._entry_netl.set_text(actions['run_netlister'][1])
        self._ckbutton_netl = gtk.CheckButton("Run netlister")
        self._ckbutton_netl.set_active(actions['run_netlister'][0])
        self._ckbutton_netl.connect('toggled', self._check_button_toggled,\
                                        self._entry_netl)
        vbox_netl.pack_start(self._ckbutton_netl)
        vbox_netl.pack_start(self._entry_netl)
        self._dlg.vbox.pack_start(vbox_netl)

        vbox_sim = gtk.VBox()
        self._entry_sim = gtk.Entry()
        self._entry_sim.set_text(actions['run_simulator'][1])
        self._ckbutton_sim = gtk.CheckButton("Run simulator")
        self._ckbutton_sim.set_active(actions['run_netlister'][0])
        self._ckbutton_sim.connect('toggled', self._check_button_toggled,\
                                        self._entry_sim)
        vbox_sim.pack_start(self._ckbutton_sim)
        vbox_sim.pack_start(self._entry_sim)
        self._dlg.vbox.pack_start(vbox_sim)
        self._ckbutton_upd = gtk.CheckButton("Update readers")
        self._ckbutton_upd.set_active(actions['update'])
        self._dlg.vbox.pack_start(self._ckbutton_upd)
        self._dlg.resize(300, 100)
        self._dlg.show_all()

    def run(self):
        actions = {}
        # 1 -> run netlister
        # 2 -> run simulator
        # 4 -> update signals
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            actions['run_netlister'] = (self._ckbutton_netl.get_active(),\
                                            self._entry_netl.get_text())
            actions['run_simulator'] = (self._ckbutton_sim.get_active(),\
                                            self._entry_sim.get_text())
            actions['update'] = self._ckbutton_netl.get_active()
        self._dlg.destroy()
        return actions

    def _check_button_toggled(self, button, entry=None):
        if entry is not None:
            entry.set_editable(button.get_active())
            print "Here", entry.get_text(), entry.get_editable(), button.get_active()
        pass
