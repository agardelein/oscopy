dnl                                                      -*-Autoconf-*-
dnl Process this file with autoconf to generate configure.
dnl
dnl The AX_* macros are defined in files in the top-level m4
dnl directory.

#####################################################################
# Set up configuration system
#####################################################################

AC_INIT([v_oscopy], [0.1], [agardelein@yahoo.fr])
AC_PROG_CC
AC_PROG_LN_S
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([
	Makefile
	src/Makefile
])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

#####################################################################
# Check for compiling & linking tools
#####################################################################

AC_PROG_CC

AC_DISABLE_STATIC
AC_PROG_LIBTOOL

AM_PROG_CC_C_O
#AX_GCC_FLAGS([-Wall])

AM_PROG_LEX
AX_PROG_AWK
AX_PROG_GROFF
AC_PATH_PROGS([M4], [gm4 m4], [m4])

#####################################################################
# Check for libraries that use pkg-config
#####################################################################
PKG_CHECK_MODULES(GLIB, [glib-2.0 >= 2.12.0], ,
  AC_MSG_ERROR([GLib 2.12.0 or later is required.]))

PKG_CHECK_MODULES(GTK, [gtk+-2.0 >= 2.10.0], ,
  AC_MSG_ERROR([GTK+ 2.10.0 or later is required.]))

#PKG_CHECK_MODULES(DBUS_GLIB, [dbus-glib-1 >= 0.74], [AC_SUBST(DBUS_LIBS)],
#  AC_MSG_ERROR([dbus-glib-1 0.74 or later is required]))
# (from pidgin-2.6.5 configure.ac)
AC_ARG_ENABLE(dbus, [AC_HELP_STRING([--disable-dbus], [disable D-Bus support])], , enable_dbus=yes)

if test "x$enable_dbus" = "xyes" ; then
	AC_CHECK_PROG(enable_dbus, dbus-binding-tool, yes, no)
fi

if test "x$enable_dbus" = "xyes" ; then
	PKG_CHECK_MODULES(DBUS, [dbus-1 >= 0.74 dbus-glib-1 >= 0.74], [
		AC_SUBST(DBUS_CFLAGS)
		AC_SUBST(DBUS_LIBS)
		enable_dbus=yes
	], [
	enable_dbus=no
	if test "x$force_deps" = "xyes" ; then
		AC_MSG_ERROR([
D-Bus development headers not found.
Use --disable-dbus if you do not need D-Bus support.
])
	fi])
fi



AC_OUTPUT
