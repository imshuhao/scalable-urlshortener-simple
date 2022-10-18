#!/bin/bash
read -p "Mode: " mode 	# add|delete
read -p "Host: " host 	# e.g. dh2020pc15

HostNum=0
File=config.properties
Lines=$(cat $File)
PORT=8848
conteenue=0

if [ $mode = "delete" ]; then
	for Line in $Lines; do
		# echo $HostNum
		# echo $Line
		if [[ $conteenue -eq 1 ]]; then
			conteenue=0
			continue
		fi
		if [[ $Line =~ $host ]]; then
			sed -i "/hostname$HostNum:$host/d" $File
			sed -i "/port$HostNum:$PORT/d" $File
			conteenue=1		# we already deleted the next line, skip the next for loop 
			echo deleted $Line
			echo deleted port$HostNum:$PORT
		elif [[ $Line =~ ^hostname ]]; then
			grep $Line $File | sed "s/hostname[0-9]+/hostname$HostNum/"
		elif [[ $Line =~ ^port ]]; then
			grep $Line $File | sed "s/port[0-9]+/port$HostNum/"
			let HostNum++	
		fi
	done
elif [ $mode = "add" ]; then
	for Line in $Lines; do
		if [[ $Line =~ ^hostname ]]; then
			let HostNum++
		fi
	done
	echo hostname$HostNum:$host >> $File
	echo port$HostNum:$PORT >> $File
else
	echo WRONG USAGE: Mode can either be add or delete!!!
fi
