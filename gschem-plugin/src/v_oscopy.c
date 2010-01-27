/* gEDA - GPL Electronic Design Automation
 * gschem - gEDA Schematic Capture
 * Copyright (C) 1998-2008 Ales Hvezda
 * Copyright (C) 1998-2008 gEDA Contributors (see ChangeLog for details)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111 USA
 */
/*#include <config.h>*/

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#ifdef HAVE_SYS_PARAM_H
#include <sys/param.h>
#endif
#include <sys/stat.h>
#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif
#ifdef HAVE_STRING_H
#include <string.h>
#endif

#include <config.h>

#include "../include/v_oscopy.h"

#ifdef HAVE_LIBDMALLOC
#include <dmalloc.h>
#endif

#ifdef HAVE_STRING_H
#include <string.h>
#endif

#include <gtk/gtk.h>

#define V_OSCOPY_NAME "oscopy"
#define V_OSCOPY_CMD "/home/agard/src/scope/oscopy_ui"
#define V_OSCOPY_MAX_STR 256

#ifdef HAVE_DBUS
#include <dbus/dbus-glib.h>

#define V_OSCOPY_DBUS_SERVICE "org.freedesktop.Oscopy"
#define V_OSCOPY_DBUS_PATH "/org/freedesktop/Oscopy"
#define V_OSCOPY_DBUS_IFACE "org.freedesktop.OscopyIFace"


gboolean v_oscopy_check(void) {
  DBusConnection *connection = NULL ;
  GError * error = NULL ;
  DBusGProxy *proxy = NULL ;

  /* Get the session bus */
  error = NULL ;
  connection = dbus_g_bus_get(DBUS_BUS_SESSION, &error) ;

  /* Make sure it is valid*/
  if( connection == NULL ) {
    g_printerr("Failed to get connection to bus: %s\n", error->message) ;
    g_error_free(error) ;
    return FALSE ;
  }

  /* Get the proxy for oscopy interface */
  proxy = dbus_g_proxy_new_for_name(connection,
				    V_OSCOPY_DBUS_SERVICE,
				    V_OSCOPY_DBUS_PATH,
				    V_OSCOPY_DBUS_IFACE) ;

  /* If no error then oscopy is there */
  if( ! error )
    return FALSE ;
  else
    return TRUE ;
}
#else

/* Return True if an instance of oscopy is running
 */
gboolean v_oscopy_check(void) {
  return FALSE ;
}
#endif

/* The viewer name
   The returned value should be freed when no longer needed
 */
void v_oscopy_get_name(gchar * name) {
  return g_strndup(V_OSCOPY_NAME, V_OSCOPY_MAX_STR) ;
}

/* The command line
   The returned value should be freed when no longer needed
 */
void v_oscopy_get_cmd(gchar * cmd) {
  return g_strndup(V_OSCOPY_CMD, V_OSCOPY_MAX_STR) ;
}

/* Return an integer identifiying the viewer
 */
void v_oscopy_get_id(void) {
  return 1 ;
}
