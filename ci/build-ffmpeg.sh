#!/bin/sh
# Build a minimal static ffmpeg for gpod-utils into PREFIX.
#
# gpod-utils packages link this instead of the distro libav*: the native aac
# encoder rewrite (NMR coder, ffmpeg 9.1) is the only good AAC encoder we can
# redistribute (libfdk_aac is non-free) and distros don't ship 9.1 yet.
#
#   ci/build-ffmpeg.sh /opt/gpod-ffmpeg
#   PKG_CONFIG_PATH=/opt/gpod-ffmpeg/lib/pkgconfig ./configure --enable-static-ffmpeg
#
# "shared" builds private shared libs instead (libavcodec-gpod.so.N, …; the
# -gpod suffix keeps them apart from distro ffmpeg) for the gpod-utils-shared
# package, where all tools share one copy instead of each embedding ~9 MB.
# It also builds ffmpeg/ffprobe programs on those libs, with the few extra
# components nasTune (https://github.com/d3vil-st/nasTune) needs - flac
# encoding (ALAC playback), image2 + scale (cover art → jpeg), dsf/webp - so
# it can use them instead of the distro ffmpeg. They find the libs via
# $ORIGIN, so they must be installed next to them:
#
#   ci/build-ffmpeg.sh /opt/gpod-ffmpeg-shared shared
#   PKG_CONFIG_PATH=/opt/gpod-ffmpeg-shared/lib/pkgconfig \
#     ./configure --with-ffmpeg-suffix=-gpod --with-ffmpeg-rpath=/usr/lib/<triplet>/gpod-utils
#
# Build deps: gcc make pkg-config git, libmp3lame dev, zlib dev, nasm (x86 only)
set -eu

PREFIX=${1:?usage: $0 <prefix> [static|shared]}
case "${2:-static}" in
  static)
    LINK="--enable-static --disable-shared --enable-pic"
    set --
    ;;
  shared)
    LINK="--disable-static --enable-shared --build-suffix=-gpod"
    # programs find the libs next to them; set via the environment because
    # configure re-evaluates --extra-ldexeflags, mangling a quoted $ORIGIN
    export LD_RUN_PATH='$ORIGIN'
    set -- --enable-ffmpeg --enable-ffprobe --disable-ffplay \
      --enable-encoder=flac --enable-muxer=image2 \
      --enable-demuxer=dsf --enable-decoder=webp --enable-parser=webp \
      --enable-filter=scale,format,null,aresample,aformat,anull
    ;;
  *) echo "usage: $0 <prefix> [static|shared]" >&2; exit 1 ;;
esac
# release/9.1 - bump to the n9.1 tag once it is cut
FFMPEG_REPO=${FFMPEG_REPO:-https://git.ffmpeg.org/ffmpeg.git}
FFMPEG_REF=${FFMPEG_REF:-f8e017db6bdac7e1d40ce24a286cf91149513877}
JOBS=${JOBS:-$(nproc)}

SRC=$(mktemp -d)
trap 'rm -rf "$SRC"' EXIT

git -C "$SRC" init -q
git -C "$SRC" fetch -q --depth 1 "$FFMPEG_REPO" "$FFMPEG_REF"
git -C "$SRC" checkout -q FETCH_HEAD

ASM=--enable-x86asm
case "$(uname -m)" in
  x86_64|i?86) ;;
  *) ASM= ;;
esac

# audio in/out for gpod-cp/extract/verify, h264/mpeg4 to probe iPod video,
# jpeg/png/bmp/gif for embedded artwork (re-encoded as mjpeg)
cd "$SRC"
./configure \
  --prefix="$PREFIX" \
  $LINK \
  --disable-programs --disable-doc --disable-network --disable-autodetect \
  --disable-everything \
  $ASM \
  --enable-zlib --enable-libmp3lame \
  --enable-swresample --enable-swscale \
  --enable-protocol=file,pipe \
  --enable-demuxer=aac,ac3,aiff,ape,asf,caf,eac3,flac,m4v,matroska,mov,mp3,ogg,tta,w64,wav,wv,h264 \
  --enable-decoder=aac,aac_fixed,aac_latm,ac3,alac,ape,eac3,flac,mp1,mp1float,mp2,mp2float,mp3,mp3float,opus,tta,vorbis,wavpack,wmalossless,wmapro,wmav1,wmav2 \
  --enable-decoder=pcm_alaw,pcm_f32be,pcm_f32le,pcm_f64be,pcm_f64le,pcm_mulaw,pcm_s16be,pcm_s16le,pcm_s24be,pcm_s24le,pcm_s32be,pcm_s32le,pcm_s8,pcm_u8 \
  --enable-decoder=h264,mpeg4,mjpeg,png,bmp,gif \
  --enable-parser=aac,aac_latm,ac3,flac,mpegaudio,opus,vorbis,h264,mpeg4video,mjpeg,png,bmp,gif \
  --enable-encoder=aac,alac,libmp3lame,mjpeg \
  --enable-muxer=adts,aiff,flac,ipod,mov,mp3,mp4,wav \
  --enable-bsf=aac_adtstoasc,null \
  "$@"
make -j"$JOBS"
make install
