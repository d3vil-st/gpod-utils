/*
 *  Copyright (C) 2021-2026 Ray <whatdoineed2do @ gmail com>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 */


/* gpod-utils helpers that need ffmpeg (audio stream hashing). Kept out of
 * gpod-utils.c so tools that never hash audio don't link ffmpeg - with the
 * static ffmpeg build any reference from gpod-utils.o pulls ~9MB into every
 * binary.
 */

#include "gpod-utils.h"
#include "gpod-ffmpeg.h"

#include <stdlib.h>

guint  gpod_hash_file(const char* path_)
{
    char*  err = NULL;
    char*  streamhash = NULL;
    guint  ret;
    if ((ret = gpod_ff_audio_hash(&streamhash, path_, &err)) == 0) {
	ret = gpod_djbhash(streamhash);
    }
    free(streamhash);
    free(err);

    return ret;
}

void   gpod_store_cksum(Itdb_Track* track_, const char* file_)
{
    track_->unk196 = gpod_hash_file(file_);
}

bool  gpod_track_fs_hash_contains(const struct gpod_track_fs_hash* htbl_, const Itdb_Track* track_, const char* path_)
{
    const guint  hash = track_->itdb ? gpod_hash(track_) : gpod_hash_file(path_);

    GSList*  what = g_hash_table_lookup(htbl_->tbl, &hash);

    return what == NULL ? false : true;
}
