#!/bin/sh

MEMORY="-Xms1024M -Xmx1280M"
JAR=" -jar ../lib/PostProcess.jar"
PROPETRIES=" ../config/Postprocess.properties*"


java $MEMORY $JAR $PROPETRIES

