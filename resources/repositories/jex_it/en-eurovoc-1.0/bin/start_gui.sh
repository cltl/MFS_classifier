#!/bin/sh

MEMORY="-Xms1024M -Xmx1280M"
JAR="-jar  ../lib/eurovoc_gui.jar"
PROPS="../config/Gui.properties"

java $MEMORY  $JAR $PROPS
