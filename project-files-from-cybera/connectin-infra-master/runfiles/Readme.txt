this is a little program for openwrt firmware to upload collectd CVS info to influxdb

install collectD , collectd-CSV collectd rrdtool, perl-system bash

copy the folder runfiles to the openwrt /  

set the open wrt to copy to the /tmp at start

make a small bash
_____________

#!/bin/bash
 cp /runfiles /tmp/runfiles

cd /tmp/runfiles
influxsend 

_________________

edit infuxsend for send frequency  default is set a ever 30 seconds (minimum)

you can set it up to every 4 hours  but if power goes out because all data is stores memory it will be lost at reboot

edit cp-csv for collectd modules you wish to send to influxdb

edit Sendinflux.pl  for your influxdb server setting

Usage: csv-to-influxdb [options] <csv-file>

  <csv-file> must be a path a to valid CSV file with an initial header row

  Options:
  --server, -s             Server address (default http://localhost:8086)
  --database, -d           Database name (default test)
  --username, -u           User name
  --password, -p           Password
  --measurement, -m        Measurement name (default data)
  --batch-size, -b         Batch insert size (default 5000)
  --tag-columns, -t        Comma-separated list of columns to use as tags
                           instead of fields
  --timestamp-column, -ts  Header name of the column to use as the timestamp
                           (default timestamp)
  --timestamp-format, -tf  Timestamp format used to parse all timestamp
                           records (default 2006-01-02 15:04:05)
  --no-auto-create, -n     Disable automatic creation of database
  --force-float, -f        Force all numeric values to insert as float
  --force-string           Force all numeric values to insert as string
  --attempts, -a           Maximum number of attempts to send data to
                           influxdb before failing
  --http-timeout, -h       Timeout (in seconds) for http writes used by
                           underlying influxdb client (default 10)
  --help
  --version, -v

  Version:
    0.1.5

  Read more:
    github.com/jpillora/csv-to-influxdb

 