#!/bin/sh

MEMORY="-Xms1024M -Xmx1280M"
JAR=" -jar ../lib/EuroVocIndexer.jar"
PROPETRIES=" ../config/Index.properties*"


java $MEMORY $JAR $PROPETRIES

