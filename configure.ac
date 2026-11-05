# autoreconf --install
# autoconf
#

AC_PREREQ([2.69])
AC_INIT([gpod-utils],[m4_esyscmd([git describe --tags --dirty --always | tr -d '\n'])],[https://github.com/whatdoineed2do/gpod-utils/issues],[https://github.com/whatdoineed2do/gpod-utils],[whatdoineed2do@nospam-github.com])
AM_INIT_AUTOMAKE([dist-bzip2 no-dist-gzip])
AC_CONFIG_MACRO_DIRS([m4])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])
AC_CONFIG_SRCDIR([src/])
AC_CONFIG_HEADERS([config.h])

AC_PROG_CC
AC_PROG_RANLIB
AC_PROG_INSTALL
PKG_PROG_PKG_CONFIG

PKG_CHECK_MODULES(GLIB, [glib-2.0])
PKG_CHECK_MODULES(GPOD, [libgpod-1.0 >= 0.8.3])
PKG_CHECK_MODULES(JSONC, [json-c >= 0.13])

AC_ARG_ENABLE(sqlite3,
	AS_HELP_STRING([--disable-sqlite3],[do not use generate db from iTunesDB]),
	[ use_sqlite3="${enableval}" ], [ use_sqlite3=yes ] )

if test "x$use_sqlite3" != xno ; then
	PKG_CHECK_MODULES(SQLITE3, sqlite3, [ use_sqlite3=yes ], [ use_sqlite3=no ])
        AH_TEMPLATE([HAVE_SQLITE3], [generate db from iTunesDB])
	AS_IF([test "x$use_sqlite3" = "xyes"], [
	        AC_DEFINE([HAVE_SQLITE3])
		AC_SUBST(SQLITE3_CFLAGS)
		AC_SUBST(SQLITE3_LIBS)
	   ])
fi
AM_CONDITIONAL([HAVE_SQLITE3], [test "x$use_sqlite3" = xyes])

AC_ARG_ENABLE(static-ffmpeg,
	AS_HELP_STRING([--enable-static-ffmpeg],[link ffmpeg statically (point PKG_CONFIG_PATH at its prefix)]),
	[ static_ffmpeg="${enableval}" ], [ static_ffmpeg=no ] )
AC_ARG_WITH(ffmpeg-suffix,
	AS_HELP_STRING([--with-ffmpeg-suffix=SFX],[ffmpeg built with --build-suffix=SFX, eg -gpod (ci/build-ffmpeg.sh <prefix> shared)]),
	[ ffsfx="${withval}" ], [ ffsfx= ] )
AS_IF([test "x$ffsfx" = xno || test "x$ffsfx" = xyes], [ffsfx=])
FFMPEG_MODULES="libavformat$ffsfx >= 58.20.100 libavcodec$ffsfx >= 58.35.100 libavutil$ffsfx >= 56.22.100 libswresample$ffsfx >= 3.3.100 libswscale$ffsfx"
AS_IF([test "x$static_ffmpeg" = xyes],
      [PKG_CHECK_MODULES_STATIC(FFMPEG, [$FFMPEG_MODULES])],
      [PKG_CHECK_MODULES(FFMPEG, [$FFMPEG_MODULES])])
PKG_CHECK_EXISTS([libavcodec$ffsfx >= 59.24.100],
		 [AC_DEFINE([HAVE_FF5_CH_LAYOUT], 1,
			    [Defined if ffmpeg/libavcodec defines new 5.1.x ch_layout])])
AC_ARG_WITH(ffmpeg-rpath,
	AS_HELP_STRING([--with-ffmpeg-rpath=DIR],[run-time path of a private shared ffmpeg (ci/build-ffmpeg.sh <prefix> shared)]),
	[ ffmpeg_rpath="${withval}" ], [ ffmpeg_rpath= ] )
dnl DT_RPATH, not RUNPATH: it also covers the libav* libs' own dependencies on each other
AS_IF([test -n "$ffmpeg_rpath" && test "x$ffmpeg_rpath" != xno],
      [FFMPEG_LIBS="$FFMPEG_LIBS -Wl,--disable-new-dtags,-rpath,$ffmpeg_rpath"])
AC_SUBST(FFMPEG_CFLAGS)
AC_SUBST(FFMPEG_LIBS)

AC_ARG_ENABLE(debug,
        AS_HELP_STRING([--enable-debug],[enable debug code (default is no)]),
        [ debug="${enableval}" ], [ debug=no ] )
if test "x$debug" = xno; then
        AC_DEFINE(NDEBUG,1,[debug code])
fi

AC_CONFIG_FILES([
Makefile
src/lib/Makefile
src/Makefile
])
AC_OUTPUT
