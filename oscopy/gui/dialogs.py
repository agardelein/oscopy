import os
import gobject
import gtk
import vte
import pty
import sys
import readline
import math

from oscopy import factors_to_names, abbrevs_to_factors

class Enter_Units_Dialog(object):
    def __init__(self):
        self._dlg = None
        self._entry_xunits = None
        self._entry_yunits = None
        self._scale_factors = gtk.ListStore(gobject.TYPE_STRING,
                                            gobject.TYPE_STRING)
        sorted_list = factors_to_names.keys()
        sorted_list.sort()
        for factor in sorted_list:
            self._scale_factors.append((factors_to_names[factor][0],
                                       factors_to_names[factor][1]))

    def display(self, units, xy, scale_factors):

        sorted_list = factors_to_names.keys()
        sorted_list.sort()
        
        self._dlg = gtk.Dialog(_('Enter graph units'),
                               flags=gtk.DIALOG_NO_SEPARATOR,
                               buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self._dlg.set_default_response(gtk.RESPONSE_ACCEPT)
        table = gtk.Table(2, 3, False)
        table.set_col_spacing(0, 12)
        table.set_col_spacing(1, 12)
        # Label, scale factor and entry for X axis
        label_xunits = gtk.Label(xy[0])
        align = gtk.Alignment(0, 0.5)
        align.add(label_xunits)
        table.attach(align, 0, 1, 0, 1)
        self._entry_xunits = gtk.Entry()
        self._entry_xunits.set_text(units[0])
        self._entry_xunits.set_width_chars(7)
        self._entry_xunits.set_activates_default(True)
        table.attach(self._entry_xunits, 2, 3, 0, 1)
        self._combox_fact = gtk.ComboBox(self._scale_factors)
        self._combox_fact.set_active(sorted_list.index(scale_factors[0]))
        cell = gtk.CellRendererText()
        self._combox_fact.pack_start(cell, True)
        self._combox_fact.add_attribute(cell, 'text', 1)
        table.attach(self._combox_fact, 1, 2, 0, 1)

        # Label, scale factor and entry for Y axis
        label_yunits = gtk.Label(xy[1])
        align = gtk.Alignment(0, 0.5)
        align.add(label_yunits)
        table.attach(align, 0, 1, 1, 2)
        self._entry_yunits = gtk.Entry()
        self._entry_yunits.set_text(units[1])
        self._entry_yunits.set_width_chars(7)
        self._entry_yunits.set_activates_default(True)
        table.attach(self._entry_yunits, 2, 3, 1, 2)
        self._comboy_fact = gtk.ComboBox(self._scale_factors)
        self._comboy_fact.set_active(sorted_list.index(scale_factors[1]))
        cell = gtk.CellRendererText()
        self._comboy_fact.pack_start(cell, True)
        self._comboy_fact.add_attribute(cell, 'text', 1)
        table.attach(self._comboy_fact, 1, 2, 1, 2)
        self._dlg.vbox.pack_start(table)

        self._dlg.show_all()

    def run(self):
        units = ()
        scale_factors = []
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            units = (self._entry_xunits.get_text(),
                     self._entry_yunits.get_text())
            x_factor_index = self._combox_fact.get_active_iter()
            y_factor_index = self._comboy_fact.get_active_iter()
            scale_factors = [self._scale_factors.get(x_factor_index, 0)[0],
                             self._scale_factors.get(y_factor_index, 0)[0]]
        self._dlg.destroy()
        return units, scale_factors

class Enter_Range_Dialog(object):
    def __init__(self):
        self._dlg = None
        self._entries = None

    def display(self, r, xy, scale_factors, units):
        self._dlg = gtk.Dialog(_('Enter graph range'),
                               flags=gtk.DIALOG_NO_SEPARATOR,
                               buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self._dlg.set_default_response(gtk.RESPONSE_ACCEPT)

        self._entries = []
        minmax = [_('From'), _('To')]
        
        hbox = gtk.HBox(False)
        for col in range(0, 2):
            frame = gtk.Frame('')
            frame.get_label_widget().set_markup('<b>'+ xy[col] +'</b>')
            frame.set_shadow_type(gtk.SHADOW_NONE)
            table = gtk.Table(1, 3, False)
            entries_row = []
            for row in range(0, 2):
                label = gtk.Label(minmax[row])
                align_lbl = gtk.Alignment(0, 0.5)
                align_lbl.add(label)
                step = abs(float(r[col][0] - r[col][1]))/100.0
                print step
                adj = gtk.Adjustment(r[col][row], -1e99, 1e99,
                                     step, step * 10.0, 0)
                entry = gtk.SpinButton(adj, 1,
                                       int(math.ceil(abs(math.log10(step)))))
                entry.set_activates_default(True)
                units_label = gtk.Label(factors_to_names[scale_factors[col]][0]
                                        + units[col])
                align_units = gtk.Alignment(0, 0.5)
                align_units.add(units_label)
                table.attach(align_lbl, 0, 1, row, row + 1, xpadding=3)
                table.attach(entry, 1, 2, row, row + 1, xpadding=3)
                table.attach(align_units, 2, 3, row, row + 1, xpadding=3)
                table.set_row_spacing(row, 6)
                entries_row.append(entry)
            self._entries.append(entries_row)
            box = gtk.HBox(False)
            box.pack_start(table, False, False, 12)
            frame.add(box)
            hbox.pack_start(frame, False, False, 0)
        self._dlg.vbox.pack_start(hbox, False, False, 6)

        self._dlg.show_all()

    def run(self):
        r = []
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            r = [str(self._entries[0][0].get_value()),
                 str(self._entries[0][1].get_value()),
                 str(self._entries[1][0].get_value()),
                 str(self._entries[1][1].get_value())]
        self._dlg.destroy()
        return r

DEFAULT_NETLISTER_COMMAND = 'gnetlist -g spice-sdb -s -o %s.net %s.sch'
DEFAULT_SIMULATOR_COMMAND = 'gnucap -b %s.net'

class Run_Netlister_and_Simulate_Dialog(object):
    def __init__(self):
        self._dlg = None
        pass

    def _make_check_entry(self, name, do_run, commands, default_command):
        # returns a tuple (check_button, combo_box_entry)
        combo = gtk.combo_box_entry_new_text()
        if not commands:
            commands = [default_command]
        for cmd in commands:
            combo.append_text(cmd)
        combo.set_active(0)
        combo.set_sensitive(do_run)

        btn = gtk.CheckButton(_('Run %s:') % name)
        btn.set_active(do_run)
        btn.connect('toggled', self._check_button_toggled, combo)
        return btn, combo

    def display(self, actions):
        self._dlg = gtk.Dialog(_("Run netlister and simulate"),
                               flags=gtk.DIALOG_NO_SEPARATOR,
                               buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self._dlg.set_default_response(gtk.RESPONSE_ACCEPT)

        # netlister part
        box = gtk.HBox()
        do_run, commands = actions['run_netlister']
        btn, combo = self._make_check_entry(_('netlister'), do_run, commands,
                                            DEFAULT_NETLISTER_COMMAND)
        self._ckbutton_netl, self._entry_netl = btn, combo
        box.pack_start(btn, False, False, 12)
        box.pack_start(combo, True, True)
        self._dlg.vbox.pack_start(box, False, False, 6)

        # simulator part
        box = gtk.HBox()
        do_run, commands = actions['run_simulator']
        btn, combo = self._make_check_entry(_('simulator'), do_run, commands,
                                            DEFAULT_SIMULATOR_COMMAND)
        self._ckbutton_sim, self._entry_sim = btn, combo
        box.pack_start(btn, False, False, 12)
        box.pack_start(combo, True, True)
        self._dlg.vbox.pack_start(box, False, False, 6)

        group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        group.add_widget(self._ckbutton_netl)
        group.add_widget(self._ckbutton_sim)

        frame = gtk.Frame('')
        frame.get_label_widget().set_markup(_('<b>Options</b>'))
        frame.set_shadow_type(gtk.SHADOW_NONE)
        vbox = gtk.VBox()
        box = gtk.HBox(False, 12)
        label = gtk.Label()
        label.set_markup(_('Run from directory:'))
        box.pack_start(label, False, False, 12)
        dialog = gtk.FileChooserDialog(_('Choose directory'),
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                       buttons=(gtk.STOCK_CANCEL,
                                                gtk.RESPONSE_REJECT,
                                                gtk.STOCK_OK,
                                                gtk.RESPONSE_ACCEPT))
        dialog.set_filename(actions['run_from'])
        self._filechoose = gtk.FileChooserButton(dialog)
        box.pack_start(self._filechoose)
        vbox.pack_start(box, False)
        box = gtk.HBox()
        self._ckbutton_upd = gtk.CheckButton(_('Update readers once terminated'))
        self._ckbutton_upd.set_active(actions['update'])
        box.pack_start(self._ckbutton_upd, False, False, 12)
        vbox.pack_start(box, False, False, 6)
        frame.add(vbox)
        self._dlg.vbox.pack_start(frame, False, False, 6)

        self._dlg.resize(400, 100)
        self._dlg.show_all()

    def _collect_data(self):
        # make sure that the command to run is always the first
        # element of the list (more recent commands are at the
        # beginning of the list) and eliminate duplicates
        netlister_cmds = [row[0] for row in self._entry_netl.get_model()]
        if self._entry_netl.get_active_text() in netlister_cmds:
            netlister_cmds.remove(self._entry_netl.get_active_text())
        netlister_cmds.insert(0, self._entry_netl.get_active_text())

        simulator_cmds = [row[0] for row in self._entry_sim.get_model()]
        if self._entry_sim.get_active_text() in simulator_cmds:
            simulator_cmds.remove(self._entry_sim.get_active_text())
        simulator_cmds.insert(0, self._entry_sim.get_active_text())

        actions = {}
        actions['run_netlister'] = (self._ckbutton_netl.get_active(), netlister_cmds)
        actions['run_simulator'] = (self._ckbutton_sim.get_active(), simulator_cmds)
        actions['update'] = self._ckbutton_upd.get_active()
        actions['run_from'] = self._filechoose.get_filename()
        return actions

    def run(self):
        actions = None
        if self._dlg.run() == gtk.RESPONSE_ACCEPT:
            actions = self._collect_data()
        self._dlg.destroy()
        return actions

    def _check_button_toggled(self, button, entry):
        entry.set_sensitive(button.get_active())
