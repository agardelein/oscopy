import os
import gtk
import vte
import pty
import sys
import readline

class Enter_Units_Dialog(object):
    def __init__(self):
        self._dlg = None
        self._entry_xunits = None
        self._entry_yunits = None
        pass

    def display(self, units):
        self._dlg = gtk.Dialog('Enter graph units',
                               buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self._dlg.set_default_response(gtk.RESPONSE_ACCEPT)
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
            units = (self._entry_xunits.get_text(),
                     self._entry_yunits.get_text())
        self._dlg.destroy()
        return units

class Enter_Range_Dialog(object):
    def __init__(self):
        self._dlg = None
        self._entries = None

    def display(self, r):
        self._dlg = gtk.Dialog('Enter graph range',
                               buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self._dlg.set_default_response(gtk.RESPONSE_ACCEPT)
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
            r = [self._entries[0][0].get_text(),
                 self._entries[0][1].get_text(),
                 self._entries[1][0].get_text(),
                 self._entries[1][1].get_text()]
        self._dlg.destroy()
        return r

class Run_Netlister_and_Simulate_Dialog:
    def __init__(self):
        self._dlg = None
        pass

    def display(self, actions):
        # Define functions to enable/disable entries upon toggle buttons
        # make window a bit larger
        self._dlg = gtk.Dialog("Run netlister and simulate",
                               flags=gtk.DIALOG_NO_SEPARATOR,
                               buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self._dlg.set_default_response(gtk.RESPONSE_ACCEPT)
        frame = gtk.Frame('')
        frame.get_label_widget().set_markup('<b>Netlister</b>')
        frame.set_shadow_type(gtk.SHADOW_NONE)
        box = gtk.HBox()
        self._entry_netl = gtk.Entry()
        self._entry_netl.set_text(actions['run_netlister'][1])
        self._ckbutton_netl = gtk.CheckButton("Run")
        self._ckbutton_netl.set_active(actions['run_netlister'][0])
        self._ckbutton_netl.connect('toggled', self._check_button_toggled,
                                    self._entry_netl)
        self._entry_netl.set_editable(self._ckbutton_netl.get_active())
        box.pack_start(self._ckbutton_netl, False, False, 12)
        box.pack_start(self._entry_netl, True, True)
        frame.add(box)
        self._dlg.vbox.pack_start(frame, False, False, 6)

        frame = gtk.Frame('')
        frame.get_label_widget().set_markup('<b>Simulator</b>')
        frame.set_shadow_type(gtk.SHADOW_NONE)
        box = gtk.HBox()
        self._entry_sim = gtk.Entry()
        self._entry_sim.set_text(actions['run_simulator'][1])
        self._ckbutton_sim = gtk.CheckButton('Run')
        self._ckbutton_sim.set_active(actions['run_simulator'][0])
        self._ckbutton_sim.connect('toggled', self._check_button_toggled,
                                   self._entry_sim)
        self._entry_sim.set_editable(self._ckbutton_sim.get_active())
        box.pack_start(self._ckbutton_sim, False, False, 12)
        box.pack_start(self._entry_sim, True, True)
        frame.add(box)
        self._dlg.vbox.pack_start(frame, False, False, 6)

        frame = gtk.Frame('')
        frame.get_label_widget().set_markup('<b>Options</b>')
        frame.set_shadow_type(gtk.SHADOW_NONE)
        vbox = gtk.VBox()
        box = gtk.HBox(False, 12)
        label = gtk.Label()
        label.set_markup('Working directory:')
        box.pack_start(label, False, False, 12)
        dialog = gtk.FileChooserDialog('Run netlister and simulator in directory...',
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
        self._ckbutton_upd = gtk.CheckButton('Update readers once terminated')
        self._ckbutton_upd.set_active(actions['update'])
        box.pack_start(self._ckbutton_upd, False, False, 12)
        vbox.pack_start(box, False)
        frame.add(vbox)
        self._dlg.vbox.pack_start(frame, False, False, 6)

        self._dlg.resize(300, 100)
        self._dlg.show_all()

    def run(self):
        resp = self._dlg.run()
        if resp == gtk.RESPONSE_ACCEPT:
            actions = {}
            actions['run_netlister'] = (self._ckbutton_netl.get_active(),
                                        self._entry_netl.get_text())
            actions['run_simulator'] = (self._ckbutton_sim.get_active(),
                                        self._entry_sim.get_text())
            actions['update'] = self._ckbutton_upd.get_active()
            actions['run_from'] = self._filechoose.get_filename()
            self._dlg.destroy()
            return actions
        else:
            self._dlg.destroy()
            return None

    def _check_button_toggled(self, button, entry=None):
        if entry is not None:
            entry.set_editable(button.get_active())

class TerminalWindow:
    def __init__(self, prompt, intro, hist_file, app_exec):
        # History file
        self.hist_file = hist_file

        # Readline configuration
        if not os.path.exists(self.hist_file):
            f = open(self.hist_file, "w")
            f.write("figlist")
            f.close()
        readline.read_history_file(self.hist_file)

        self.prompt = prompt
        self.intro = intro
        self._term = None
        self._app_exec = app_exec
        self.is_there = False
        self._term_hist_item = readline.get_current_history_length() + 1

    def create(self):
        cmdw = gtk.Window()
        if self._term is None:
            self._term = vte.Terminal()
            self._term.set_cursor_blinks(True)
            self._term.set_emulation('xterm')
            self._term.set_font_from_string('monospace 9')
            self._term.set_scrollback_lines(1000)
            self._term.show()
            (master, slave) = pty.openpty()
            self._term.set_pty(master)
            sys.stdout = os.fdopen(slave, "w")
            print self.intro
	scrollbar = gtk.VScrollbar()
	scrollbar.set_adjustment(self._term.get_adjustment())
        
	termbox = gtk.HBox()
	termbox.pack_start(self._term)
	termbox.pack_start(scrollbar)

        entrybox = gtk.HBox(False)
        label = gtk.Label('Command:')
        entry = gtk.Entry()
        entry.connect('activate', self._entry_activate)
        entry.connect('key-press-event', self._entry_key_pressed)
        entrybox.pack_start(label, False, False, 12)
        entrybox.pack_start(entry, True, True, 12)

        box = gtk.VBox()
        box.pack_start(termbox)
        box.pack_start(entrybox)

        cmdw.connect('destroy', self._destroy)
        cmdw.add(box)
        cmdw.show_all()
        self.is_there = True

    def _destroy(self, data=None):
        self.is_there = False
        return False
        
    def _entry_activate(self, entry, data=None):
        if isinstance(entry, gtk.Entry):
            line = entry.get_text()
            if line is not None:
                print self.prompt + line
                self._app_exec(line)
                readline.add_history(line)
            self._term_hist_item = readline.get_current_history_length()
            entry.set_text('')

    def _entry_key_pressed(self, entry, event):
        if gtk.gdk.keyval_name(event.keyval) == "Up":
            line = readline.get_history_item(self._term_hist_item - 1)
            if line is not None:
                self._term_hist_item = self._term_hist_item - 1
                entry.set_text(line)
            return True
        elif gtk.gdk.keyval_name(event.keyval) == "Down":
            line = readline.get_history_item(self._term_hist_item + 1)
            if line is not None:
                self._term_hist_item = self._term_hist_item + 1
                entry.set_text(line)
            return True

