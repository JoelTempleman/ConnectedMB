#!/bin/bash


printenv | sed 's/^\(.*\)$/export \1/g' > /etc/.env.sh
chmod +x /etc/.env.sh

cron -f && tail -f /var/log/cron.log
