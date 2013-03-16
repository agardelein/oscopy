## ipython.m4 - Check for IPython version on a system. -*-Autoconf-*-
## Copyright (C) 2013 Arnaud Gardelein.
## Author: Arnaud Gardelein <arnaud@oscopy.org>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## As a special exception to the GNU General Public License, if you
## distribute this file as part of a program that contains a
## configuration script generated by Autoconf, you may include it under
## the same distribution terms that you use for the rest of that program.

# AM_PATH_IPYTHON([MINIMUM-VERSION], [ACTION-IF-FOUND], [ACTION-IF-NOT-FOUND])
# ---------------------------------------------------------------------------
# Adds support for distributing IPYTHON modules and packages. 
#
# If the MINIMUM-VERSION argument is passed, AM_PATH_IPYTHON will
# cause an error if the version of IPYTHON installed on the system
# doesn't meet the requirement.  MINIMUM-VERSION should consist of
# numbers and dots only.

# check also matplotlib, numpy, dbus, xdg, gtk
AC_DEFUN([AM_PATH_IPYTHON],
 [
  dnl Find a IPYTHON interpreter.
  m4_define_default([_AM_IPYTHON_INTERPRETER_LIST],
[ipython])

  AC_ARG_VAR([IPYTHON], [the IPython interpreter])

  m4_if([$1],[],[
    dnl No version check is needed.
    # Find any IPython interpreter.
    if test -z "$IPYTHON"; then
      AC_PATH_PROGS([IPYTHON], _AM_IPYTHON_INTERPRETER_LIST, :)
    fi
    am_display_IPYTHON=IPython
  ], [
    dnl A version check is needed.
    if test -n "$IPYTHON"; then
      # If the user set $IPYTHON, use it and don't search something else.
      AC_MSG_CHECKING([whether $IPYTHON version >= $1])
      AM_IPYTHON_CHECK_VERSION([$IPYTHON], [$1],
			      [AC_MSG_RESULT(yes)],
			      [AC_MSG_ERROR(too old)])
      am_display_IPYTHON=$IPYTHON
    else
      # Otherwise, try each interpreter until we find one that satisfies
      # VERSION.
      AC_CACHE_CHECK([for a IPython interpreter with version >= $1],
	[am_cv_pathless_IPYTHON],[
	for am_cv_pathless_IPYTHON in _AM_IPYTHON_INTERPRETER_LIST none; do
	  test "$am_cv_pathless_IPYTHON" = none && break
	  AM_IPYTHON_CHECK_VERSION([$am_cv_pathless_IPYTHON], [$1], [break])
	done])
      # Set $IPYTHON to the absolute path of $am_cv_pathless_IPYTHON.
      if test "$am_cv_pathless_IPYTHON" = none; then
	IPYTHON=:
      else
        AC_PATH_PROG([IPYTHON], [$am_cv_pathless_IPYTHON])
      fi
      am_display_IPYTHON=$am_cv_pathless_IPYTHON
    fi
  ])

  if test "$IPYTHON" = :; then
  dnl Run any user-specified action, or abort.
    m4_default([$3], [AC_MSG_ERROR([no suitable IPython interpreter found])])
  else

  dnl Query IPYTHON for its version number.

  AC_CACHE_CHECK([for $am_display_IPYTHON version], [am_cv_ipython_version],
    [am_cv_ipython_version=`$IPYTHON -c "import IPython,sys; sys.stdout.write(IPython.release.version if hasattr(IPython, 'release') else IPython.Release.version)"`])
  AC_SUBST([IPYTHON_VERSION], [$am_cv_ipython_version])

  dnl Use the values of $prefix and $exec_prefix for the corresponding
  dnl values of IPYTHON_PREFIX and IPYTHON_EXEC_PREFIX.  These are made
  dnl distinct variables so they can be overridden if need be.  However,
  dnl general consensus is that you shouldn't need this ability.

  dnl AC_SUBST([IPYTHON_PREFIX], ['${prefix}'])
  dnl AC_SUBST([IPYTHON_EXEC_PREFIX], ['${exec_prefix}'])

  dnl At times (like when building shared libraries) you may want
  dnl to know which OS platform IPYTHON thinks this is.

  dnl AC_CACHE_CHECK([for $am_display_IPYTHON platform], [am_cv_IPYTHON_platform],
  dnl  [am_cv_IPYTHON_platform=`$IPYTHON -c "import sys; sys.stdout.write(sys.platform)"`])
  dnl AC_SUBST([IPYTHON_PLATFORM], [$am_cv_IPYTHON_platform])
  dnl Run any user-specified action.
  $2
  fi
])

# AM_IPYTHON_CHECK_VERSION(PROG, VERSION, [ACTION-IF-TRUE], [ACTION-IF-FALSE])
# ---------------------------------------------------------------------------
# Run ACTION-IF-TRUE if the IPYTHON interpreter PROG has version >= VERSION.
# Run ACTION-IF-FALSE otherwise.
AC_DEFUN([AM_IPYTHON_CHECK_VERSION],
 [prog="import sys, IPython;minver = list(map(int, '$2'.split('.'))) + [[0, 0, 0]];ver = list(map(int, (IPython.release.version if hasattr(IPython, 'release') else IPython.Release.version).split('.')[[0:3]])) + [[0, 0, 0]];minverhex = sum([[minver[i]<<((4-i)*8) for i in range(0, 4)]]);verhex = sum([[ver[i]<<((4-i)*8) for i in range(0, 4)]]);sys.stdout.write('1' if verhex < minverhex else '0');"
  AS_IF([AM_RUN_LOG_IPYTHON([$1 -c "$prog"])], [$3], [$4])])

# AM_RUN_LOG_IPYTHON(COMMAND)
# -------------------
# Run COMMAND, save the output in ac_status, and log it.
# (This has been adapted from Python's AM_RUN_LOG macro.)
AC_DEFUN([AM_RUN_LOG_IPYTHON],
[{ echo "$as_me:$LINENO: $1" >&AS_MESSAGE_LOG_FD
#   ($1) >&AS_MESSAGE_LOG_FD 2>&AS_MESSAGE_LOG_FD
    # First check whether the program exists
    # Probably /dev/null is not portable ouside linux systems...
   which `echo $1 | cut -d ' ' -f 1` > /dev/null
   if test "$?" = 1; then
      ac_status=1
      (exit $ac_status);
   else
      ac_status=`$*`
      echo "$as_me:$LINENO: \$? = $ac_status" >&AS_MESSAGE_LOG_FD
      (exit $ac_status);
   fi
 }])
