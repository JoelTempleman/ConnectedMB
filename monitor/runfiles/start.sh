cp -r /runfiles /tmp
echo "starting"
sleep 10
/tmp/runfiles/./influxsend & /tmp/runfiles/./influxsend2 
