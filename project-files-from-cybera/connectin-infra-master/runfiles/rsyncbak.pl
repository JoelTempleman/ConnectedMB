#!/usr/bin/perl
#use strict;
use warnings;

use 5.010;
my $rec = `/sbin/ifconfig -a | grep "HWaddr"`;
my ($field1, $field2, $field3, $field4, $mac) = split(/\s+/, $rec);
$mac =~ tr/:/-/;

my $HostName = `cat /proc/sys/kernel/hostname`;

print "$mac   $HostName";

`rsync -e "ssh -p 22 -i /root/.ssh/id_rsa" -brvup  /tmp/OpenWrt/ "owner@172.16.3.228:/home/owner/BACKUPS"`;

