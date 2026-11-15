#!/bin/bash
# strip.sh in.mp4 out.mp4 : Regel 19 – neu kodieren, alle Metadaten entfernen, x264-SEI raus, Encoder-Tags leer
set -e
IN=$1; OUT=$2; TMP=${OUT%.mp4}_tmp.mp4
ffmpeg -y -loglevel error -i "$IN" -map 0:v -map 0:a -map_metadata -1 -map_chapters -1 -c:v libx264 -crf 18 -preset veryfast -x264-params no-info=1 -bsf:v filter_units=remove_types=6 -c:a aac -b:a 192k -fflags +bitexact -flags:v +bitexact -flags:a +bitexact -metadata:s:v encoder= -metadata:s:a encoder= -movflags +faststart "$TMP"
ffmpeg -y -loglevel error -i "$TMP" -map 0 -c copy -map_metadata -1 -fflags +bitexact -flags +bitexact -metadata:s:v encoder= -metadata:s:a encoder= -movflags +faststart "$OUT"
rm -f "$TMP"
