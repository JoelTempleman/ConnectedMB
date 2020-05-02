#!/bin/sh

currentDate=`date`
echo "$currentDate: runnning $(basename $(readlink -nf $0))"

source "/etc/.env.sh"

python3 /home/connectin/migration_backup/backup_to_csv.py
