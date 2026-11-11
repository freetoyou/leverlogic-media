#!/bin/bash
# mix.sh <videoordner> <dateiname>  -> <name>.mp4 (eine Datei für alle Plattformen)
# v3.4: Musik hörbar, weiches Ducking. v5 (01.11.2026): Ton um 0,1 s verschoben, weil das Thumbnail die ersten 0,1 s belegt.
set -e
# 11.11.2026: ohne Thumbnail-Frame kein Ton-Versatz. DELAY=100 nur zusammen mit THUMB=3.
D=${DELAY:-0}
V=$1; N=$2; cd $V/build
python3 /home/claude/shared/audio.py $V > /dev/null
ffmpeg -y -loglevel error -i voice44.wav -i music.wav -i sfx.wav -filter_complex "[1:a][0:a]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400[m];[0:a][m][2:a]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=11,adelay=${D}:all=1[a]" -map "[a]" -ar 44100 -ac 2 mix.wav
ffmpeg -y -loglevel error -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest $N.mp4
[ -f thumbnail.png ] && cp thumbnail.png ${N}_thumbnail.png || true
ffprobe -v error -show_entries format=duration -of csv=p=0 $N.mp4
