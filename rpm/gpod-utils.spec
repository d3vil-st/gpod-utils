Name:           gpod-utils
Version:        %{_version}
Release:        1%{?dist}
Summary:        Command line tools using libgpod to access iPod data

License:        GPL-2.0-or-later
URL:            https://github.com/whatdoineed2do/gpod-utils
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc make
BuildRequires:  autoconf automake libtool
BuildRequires:  pkgconfig
BuildRequires:  libgpod-devel
BuildRequires:  glib2-devel
# --define "ffmpeg_prefix <dir>" links the static ffmpeg built by ci/build-ffmpeg.sh
%if 0%{?ffmpeg_prefix:1}
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

%prep
%setup -q

%build
autoreconf --install
%if 0%{?ffmpeg_prefix:1}
export PKG_CONFIG_PATH=%{ffmpeg_prefix}/lib/pkgconfig
%configure --enable-static-ffmpeg
%else
%configure
%endif
%make_build

%install
%make_install

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

%changelog
* Mon Nov 02 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.6.1-1
- gpod-cp: add -X/--transcode-lossless

* Mon Nov 02 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.6.0-1
- Link a static ffmpeg 9.1 (new native AAC encoder); prefer it over mp3 when libfdk_aac is unavailable

* Sat Jun 13 2026 Ilya Kargapolov <d3vil.st@gmail.com> - 1.4.4-1
- Initial RPM packaging
