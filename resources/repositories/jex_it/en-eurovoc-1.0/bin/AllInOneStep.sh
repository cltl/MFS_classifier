#!/bin/sh

MEMORY="-Xms1024M -Xmx1280M"

PRE_PROCESS_JAR=" -jar ../lib/CreateCompactFormat.jar"
PRE_PROCESS_PROPERTIES="  ../config/PreProcess.properties"

INDEXER_JAR=" -jar  ../lib/EuroVocIndexer.jar"
INDEXER_PROPERTIES="../config/Index.properties"

POST_PROCESS_INDEXER="  -jar ../lib/PostProcess.jar"
POST_PROCESS_PROPETRIES=" ../config/Postprocess.properties"

echo "PreProcessing ....\n"
java  $PRE_PROCESS_JAR $PRE_PROCESS_PROPERTIES


echo Indexing .....
java $MEMORY $INDEXER_JAR  $INDEXER_PROPERTIES


echo Post processing .....
java $MEMORY $POST_PROCESS_INDEXER $POST_PROCESS_PROPETRIES
