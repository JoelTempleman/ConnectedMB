#!/usr/bin/perl
#use strict;
use warnings;


use 5.010;

use Net::Ping;
my $p = Net::Ping->new();
if ($p->ping('172.16.3.228')) {
       say 'Influx Sever Online';
    } else {
   say 'Influx Server Offine';
exit;
}


#`cd /tmp/runfiles/tmp2/`;

my $rec = `/sbin/ifconfig -a | grep "HWaddr"`;
my ($field1, $field2, $field3, $field4, $mac) = split(/\s+/, $rec);
$mac =~ tr/:/-/;
`/tmp/runfiles/./cp-INT`;
@files = <*>;
 foreach $file (@files) {
  if($file =~ m/\.csv/) {
@filename1 = split('\.cs', $file);
    @filename = split('\-20', $filename1[0]);
    $name = $filename[0];

`mv $file $name.csv`;
`echo "1" > test.csv.csv`;

`rm *.csv.csv`;

print "$name ";    
 `/tmp/runfiles/tmp2/./awk-int -f $name.csv`;   
#$names=${name%-2*};
#print "$names";    
      `/tmp/runfiles/CSV/./csv-to-influxdb --batch-size=5000 --server=http://172.16.3.228:8086 --database=$mac --measurement=$name /tmp/runfiles/CSV-INT/$name.csv `;
  }
}
print "\ndone :)";
`rm /tmp/runfiles/tmp2/*.csv`;
`rm /tmp/runfiles/CSV-INT/*.csv`;
