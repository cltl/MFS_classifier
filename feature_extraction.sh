
#relevant paths
export cwd=/${PWD#*/}
export extracted_features=$cwd/resources/extracted_features

mkdir -p $extracted_features

#sval2013
python extract_features.py -c "sval2013" --rem_mon > $extracted_features/sval2013.csv 2> $extracted_features/sval2013.csv.err

#sval2015
python extract_features.py -c "sval2015" --rem_mon > $extracted_features/sval2015.csv 2> $extracted_features/sval2015.csv.err

#semcor
python extract_features.py -c "semcor"   --rem_mon > $extracted_features/semcor.csv 2> $extracted_features/semcor.csv.err
