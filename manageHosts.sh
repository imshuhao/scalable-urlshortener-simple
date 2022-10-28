#!/bin/bash
read -p "Mode: " mode 	# add|delete
read -p "Host: " host 	# e.g. dh2020pc15

HostNum=0
File=config.properties
Lines=$(cat $File)
PORT=8848
conteenue=0
lineNum=1

if [ $mode = "delete" ]; then
	for Line in $Lines; do
		if [[ $conteenue -eq 1 ]]; then
			conteenue=0
			continue
		fi
		if [[ $Line =~ $host ]]; then
			ssh $host "pgrep URLShortner.py | xargs -r kill" &
			sed -i "/hostname$HostNum:$host/d" $File
			sed -i "/port$HostNum:$PORT/d" $File
			conteenue=1		# we already deleted the next line, skip the next for loop 
			echo deleted $Line
			echo deleted port$HostNum:$PORT
		elif [[ $Line =~ ^hostname ]]; then
			newHost=`echo $Line | sed "s/hostname[0-9]\+/hostname$HostNum/"`
			sed -i "s/$Line/$newHost/" $File
		elif [[ $Line =~ ^port ]]; then
			newPort=`echo $Line | sed "s/port[0-9]\+/port$HostNum/"`
			sed -i "s/$Line/$newPort/" $File
			let HostNum++	
		fi

	done
elif [ $mode = "add" ]; then
	for Line in $Lines; do
		if [[ $Line =~ ^hostname ]]; then
			let HostNum++
		fi
	done
	if [[ $host =~ "dh20" ]]; then
		echo hostname$HostNum:$host >> $File
		echo port$HostNum:$PORT >> $File
	else
		echo Unknown Host
	fi
else
	echo WRONG USAGE: Mode can either be add or delete!!!
fi
