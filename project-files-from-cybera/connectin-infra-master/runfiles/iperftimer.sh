#sleep 40 
#cd /tmp/runfiles/
IR="$(head -30 /dev/urandom |tr -dc "0123456789" | head -c2)"
DELAY=13320
MULT=3
IR1="$(($IR * $MULT))"
IT="$(($IR1 +$DELAY))"
echo $IT
/runfiles/./timer.pl $IT /runfiles/./iperfrsync
