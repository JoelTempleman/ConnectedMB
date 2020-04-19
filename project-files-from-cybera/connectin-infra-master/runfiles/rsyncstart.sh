cp -r /runfiles /tmp
echo "starting"
sleep 10
/tmp/runfiles/./timer.pl 30 /tmp/runfiles/./brsync ## >> /tmp/br.log
