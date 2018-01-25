#!/bin/sh

TABCOUNTER=0

while [ 1 ]; do
	WAIT="$(grep -m1 -ao '[0-9]' /dev/urandom | sed s/0/10/ | head -n1)"
	
	if [ $TABCOUNTER -eq 0 ]
	then
		WAIT=$(($WAIT+2))
	else
		WAIT=$(($WAIT+6))
		WAIT=$(expr $WAIT / 3)
	fi
	google-chrome --incognito http://www.webpage.com
	sleep $WAIT
	# La commande pour le replay
	cnee --replay -f vote.xnl
	TABCOUNTER=$(expr $TABCOUNTER + 1)

	if [ $TABCOUNTER -eq 10 ]
	then
		sleep 2
		cnee --replay -f closeWindow.xnl
		TABCOUNTER=0
	fi

done 

# participants
