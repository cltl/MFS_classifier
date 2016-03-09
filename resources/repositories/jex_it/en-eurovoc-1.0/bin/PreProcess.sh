#!/bin/sh

MEMORY="-Xms1024M -Xmx1280M"
JAR="-jar ../lib/CreateCompactFormat.jar"
PROPETRIES="../config/PreProcess.properties"


java $MEMORY $JAR $PROPETRIES

