dnl                                                      -*-Autoconf-*-
dnl Process this file with autoconf to generate configure.
dnl
dnl The AX_* macros are defined in files in the top-level m4
dnl directory.

#####################################################################
# Set up configuration system
#####################################################################

AC_INIT([oscopy], [0.32], [agardelein@yahoo.fr])
AC_CONFIG_AUX_DIR([build-tools])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

AC_PROG_LN_S
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_FILES([
	Makefile
	oscopy/Makefile
	oscopy/graphs/Makefile
	oscopy/readers/Makefile
	oscopy/writers/Makefile
	oscopy/gui/Makefile
	scheme/Makefile
])

#####################################################################
# Check for compiling & linking tools
#####################################################################

AC_PATH_PROGS([M4], [gm4 m4], [m4])
AM_PATH_PYTHON([2.5])

#####################################################################
# Check for libraries that use pkg-config
#####################################################################

PKG_PROG_PKG_CONFIG

PKG_CHECK_MODULES(PYGTK, [pygtk-2.0 >= 2.10.0], ,
  AC_MSG_ERROR([PyGTK 2.10.0 or later is required.]))

AC_OUTPUT
