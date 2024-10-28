#!/bin/bash -l

logdir=~/.bluebot/logs/
log="$logdir/bluebot$(date "+%U").log"
args=
#args=--dry

cd ~/work/git/bluebot
. venv/bin/activate

date >> $log

python3 -m bluebot \
  -l ~/.bluebot/login.conf \
  -s ~/.bluebot/schedule/schedule.conf \
  -t ~/.bluebot/timestamp.txt \
  $args \
  >> "$log" 2>&1

find "$logdir" -type f -mtime +30 -delete