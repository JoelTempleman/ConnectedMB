#!/usr/bin/perl
binmode STDOUT, ":utf8";
use utf8;
 

my $rec = `/sbin/ifconfig -a | grep "HWaddr"`;
my ($field1, $field2, $field3, $field4, $mac) = split(/\s+/, $rec);
$mac =~ tr/:/-/;
my $speed = `./speedtest-csv`;
print "$speed";
#cd /var/www/html/runfile/
open CSV, ">/tmp/runfiles/CSV/speedtest.csv";
print CSV "timestamp, Provider, IP, Test_Server, province, Ping, Download, Upload" ;

print CSV "\n$speed";
  

close CSV;
`/tmp/runfiles/CSV/./csv-to-influxdb --batch-size=1000 --server=http://172.16.3.228:8086 --database=$mac --measurement=speedtest /tmp/runfiles/CSV/speedtest.csv `;
 open CSVARC, ">>/tmp/runfiles/speedtest.csv";
 print CSVARC "$speed";
 close CSVARC;
print "\ndone > ";
