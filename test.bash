#!/bin/bash

javac URLShortner.java
java -classpath ".:sqlite-jdbc-3.39.3.0.jar" URLShortner.java 8851 &
java -classpath ".:sqlite-jdbc-3.39.3.0.jar" URLShortner.java 8852 &
java -classpath ".:sqlite-jdbc-3.39.3.0.jar" URLShortner.java 8853 &
java -classpath ".:sqlite-jdbc-3.39.3.0.jar" URLShortner.java 8854 &