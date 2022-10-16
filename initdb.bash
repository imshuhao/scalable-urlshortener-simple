#!/bin/bash

# rm ./urlMap.db
sqlite3 ./urlMap.db < schema.sql

javac Initdb.java
java -classpath ".:sqlite-jdbc-3.39.3.0.jar" Initdb.java "jdbc:sqlite:./urlMap.db"