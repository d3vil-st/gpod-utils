# Two variants from this spec (separate rpmbuild runs, they conflict):
#   --define "ffmpeg_prefix <dir>"         gpod-utils, static ffmpeg in each tool
#                                          (ci/build-ffmpeg.sh <dir>)
#   --define "ffmpeg_shared_prefix <dir>"  gpod-utils-shared, one private shared
#                                          ffmpeg in %{_libdir}/gpod-utils
#                                          (ci/build-ffmpeg.sh <dir> shared)
%if 0%{?ffmpeg_shared_prefix:1}
Name:           gpod-utils-shared
Conflicts:      gpod-utils
%global gpod_ff_libdir %{_libdir}/gpod-utils
%else
Name:           gpod-utils
Conflicts:      gpod-utils-shared
%endif
Version:        %{_version}
Release:        1%{?dist}
Summary:        Command line tools using libgpod to access iPod data

License:        GPL-2.0-or-later
URL:            https://github.com/whatdoineed2do/gpod-utils
Source0:        gpod-utils-%{version}.tar.gz

BuildRequires:  gcc make
BuildRequires:  autoconf automake libtool
BuildRequires:  pkgconfig
BuildRequires:  libgpod-devel
BuildRequires:  glib2-devel
%if 0%{?ffmpeg_prefix:1}%{?ffmpeg_shared_prefix:1}
BuildRequires:  lame-devel
BuildRequires:  zlib-devel
%else
BuildRequires:  ffmpeg-devel
%endif
BuildRequires:  json-c-devel
BuildRequires:  sqlite-devel

%description
Command line tools using libgpod to access iPod data.
Provides utilities for listing, copying, removing, tagging, and verifying
iPod tracks from the command line.
%if 0%{?ffmpeg_shared_prefix:1}

This variant links all tools against one private copy of ffmpeg's shared
libraries instead of a static ffmpeg in every tool. ffmpeg and ffprobe
programs built on the same libraries are installed alongside them (not on
PATH) for nasTune.
%endif

%prep
%setup -q -n gpod-utils-%{version}

%build
autoreconf --install
%if 0%{?ffmpeg_shared_prefix:1}
export PKG_CONFIG_PATH=%{ffmpeg_shared_prefix}/lib/pkgconfig
%configure --with-ffmpeg-suffix=-gpod --with-ffmpeg-rpath=%{gpod_ff_libdir}
%elif 0%{?ffmpeg_prefix:1}
export PKG_CONFIG_PATH=%{ffmpeg_prefix}/lib/pkgconfig
%configure --enable-static-ffmpeg
%else
%configure
%endif
%make_build

%install
%make_install
%if 0%{?ffmpeg_shared_prefix:1}
install -d %{buildroot}%{gpod_ff_libdir}
cp -a %{ffmpeg_shared_prefix}/lib/lib*-gpod.so.* \
      %{ffmpeg_shared_prefix}/bin/ffmpeg %{ffmpeg_shared_prefix}/bin/ffprobe \
      %{buildroot}%{gpod_ff_libdir}/
%endif

%files
%{_bindir}/gpod
%{_bindir}/gpod-cp
%{_bindir}/gpod-extract
%{_bindir}/gpod-hashsum
%{_bindir}/gpod-ls
%{_bindir}/gpod-playlist
%{_bindir}/gpod-rm
%{_bindir}/gpod-tag
%{_bindir}/gpod-verify
%if 0%{?ffmpeg_shared_prefix:1}
%{gpod_ff_libdir}/
%endif

%changelog
* Thu Nov 05 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.6.3-1
- gpod-utils-shared: ship private ffmpeg/ffprobe programs for nasTune

* Thu Nov 05 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.6.2-1
- New gpod-utils-shared variant: tools share one private shared ffmpeg
- gpod-tag/gpod-playlist no longer link ffmpeg

* Mon Nov 02 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.6.1-1
- gpod-cp: add -X/--transcode-lossless

* Mon Nov 02 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.6.0-1
- Link a static ffmpeg 9.1 (new native AAC encoder); prefer it over mp3 when libfdk_aac is unavailable

* Sat Jun 13 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.4.4-1
- Initial RPM packaging
