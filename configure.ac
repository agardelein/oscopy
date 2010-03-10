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
AC_PROG_CC
AC_PROG_LN_S
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([
	Makefile
	oscopy/Makefile
	oscopy/graphs/Makefile
	oscopy/readers/Makefile
	oscopy/writers/Makefile
	oscopy_gui/Makefile
])

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
AM_PATH_PYTHON([2.5])

#####################################################################
# Check for libraries that use pkg-config
#####################################################################


AC_OUTPUT
