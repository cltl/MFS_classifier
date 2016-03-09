@echo off

echo PreProcessing ....
echo.
java -Xms1400M  -jar  ../lib/CreateCompactFormat.jar ../config/PreProcess.properties
echo.
echo Indexing .....
echo.
java -Xms1400M  -jar  ../lib/EuroVocIndexer.jar ../config/Index.properties
echo.
echo Post processing .....
echo.
java -Xms1400M -jar ../lib/PostProcess.jar ../config/Postprocess.properties

