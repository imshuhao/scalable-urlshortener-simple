#!/bin/bash

javac URLShortner.java
java -classpath ".:sqlite-jdbc-3.39.3.0.jar" URLShortner.java
