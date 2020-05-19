#!/usr/bin/perl
#use strict;
use warnings;

use 5.010;

sub GetServerAddress {

    use File::Spec;                                                                               
                                                                                                   
    if ( not "/tmp/runfiles/" ) {                                                                  
       die qq(Directory doesn't exist);                                                            
    }                                                                                              
                                                                                                   
    my $filePath = "/tmp/runfiles/serverlist";                                                     
                                                                                                   
    open( my $fileHandle, "<", $filePath )                                                         
       or die qq(Cannot open $filePath for reading! $!);                                           
                                                                                                   
    my $test_sequence_value;                                                                       
    while( my $line = <$fileHandle> ) {                                                            
        chomp $line;                                                                               
        next unless $line =~ /^\s*DBASE\s*=\s*(.*)\s*/;                                            
        $test_sequence_value = $1;                                                                 
        last;                                                                                      
    }                                                                                              
    close $fileHandle;                                                                             
    if ( defined $test_sequence_value ) {                                                          
        # Whatever you do if you find that value...                                                
        return $test_sequence_value;                                                               
    }                                                                                              
    else {                                                                                         
        # Whatever you do if the value isn't found...                                              
        return;                                                                                    
    }                                                                                              
}                                                                                                  
                                                                                                   
my $IP = GetServerAddress();                                                                       
                                                                                                   
use Net::Ping;                                                                                     
                                                                                                   
open OUTPUTS, ">>", "/debug/logfile" or die $!;                                                    
                                                                                                   
my $p = Net::Ping->new();                                                                          
if ($p->ping( $IP )) {                                                                             
       say "SendINT Influx Server Online at $IP";                                                  
       print OUTPUTS "SendINT Influx Server Online at $IP\n";                                      
    } else {                                                                                       
   say "SendINT Influx Server OFFLINE at $IP";                                                     
   print OUTPUTS "SendINT Influx Server OFFLINE at $IP\n";                                         
exit;                                                                                              
}                                                                                                  
                                                                                                   
close(OUTPUTS);   

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
      `/tmp/runfiles/CSV/./csv-to-influxdb --batch-size=5000 --server=http://$IP:8086 --database=$mac --measurement=$name /tmp/runfiles/CSV-INT/$name.csv `;
  }
}
print "\ndone :)";
`rm /tmp/runfiles/tmp2/*.csv`;
`rm /tmp/runfiles/CSV-INT/*.csv`;
