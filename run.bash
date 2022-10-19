#!/bin/bash

rm -r /virtual/dongshu4/URLShortner/
mkdir -p /virtual/dongshu4/URLShortner
cp urlMap.db /virtual/dongshu4/URLShortner/

pkill java
javac URLShortner.java
java -classpath ".:sqlite-jdbc-3.39.3.0.jar" URLShortner.java &
