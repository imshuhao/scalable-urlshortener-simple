#!/bin/bash
# SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd ) # https://stackoverflow.com/questions/255898/how-to-iterate-over-arguments-in-a-bash-script
# cd $SCRIPT_DIR

rm -r /virtual/dongshu4/URLShortner/
mkdir -p /virtual/dongshu4/URLShortner
cp urlMap.db /virtual/dongshu4/URLShortner/


/opt/jdk-18.0.2/bin/javac URLShortner.java
/opt/jdk-18.0.2/bin/java -classpath ".:sqlite-jdbc-3.39.3.0.jar" URLShortner.java &
