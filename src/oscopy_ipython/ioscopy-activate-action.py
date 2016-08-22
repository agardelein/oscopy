#!/usr/bin/python3

import sys, dbus

OSCOPY_DBUS_NAME = 'org.gtk.oscopy'
OSCOPY_DBUS_PATH = '/org/gtk/oscopy'
GTK_ACTION_IFACE = 'org.gtk.Actions'
SUPPORTED_ACTIONS = ['update_files']

if len(sys.argv) != 2:
    print('Usage : %s <action>' % sys.argv[0])
    sys.exit(-1)

# Initialize DBUS, get the interface
try:
    bus = dbus.SessionBus()
except dbus.DBusException as e:
    print('DBus not available:', e)
    sys.exit(-1)
oscopy = bus.get_object(OSCOPY_DBUS_NAME, OSCOPY_DBUS_PATH)
oscopy_iface = dbus.Interface(oscopy, dbus_interface=GTK_ACTION_IFACE)

m = oscopy_iface.get_dbus_method('Activate')

action_name = sys.argv[1]

if action_name in SUPPORTED_ACTIONS:
    m(dbus.String(action_name), dbus.Array(dbus.String('', variant_level=1)), dbus.Dictionary({'':dbus.String('')}))
sys.exit(0)
