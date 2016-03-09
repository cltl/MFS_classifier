export cwd=/${PWD#*/}


#create identifier sval2013 and save them
export input_path=$cwd/resources/scorers/semeval-2013-task12-test-data/keys/gold/wordnet/wordnet.en.key
export sval2013_bin=$cwd/resources/identifiers/sval2013.bin
python scripts/get_identifiers.py -c "sval2013" -i $input_path -o $sval2013_bin

#create identifier sval2015 and save them
export input_path=$cwd/resources/scorers/SemEval-2015-task-13-v1.0/keys/gold_keys/EN/semeval-2015-task-13-en.key
export sval2015_bin=$cwd/resources/identifiers/sval2015.bin
python scripts/get_identifiers.py -c "sval2015" -i $input_path -o $sval2015_bin

#jex
export output_jex=$cwd/resources/repositories/jex_it/jex_output
export semcor_naf=$cwd/resources/wsd_corpora/semcor1.6
export sval2013_naf=$cwd/resources/wsd_corpora/semeval2013_task12
export sval2015_naf=$cwd/resources/wsd_corpora/semeval2015_task13_en
export jex_semcor=$cwd/resources/feature_input/jex_semcor.bin
export jex_sval2013=$cwd/resources/feature_input/jex_sval2013.bin
export jex_sval2015=$cwd/resources/feature_input/jex_sval2015.bin
export jex_folder=$cwd/resources/repositories/jex_it/en-eurovoc-1.0

#run jex for semcor
export output_path=$cwd/resources/feature_input/train_semcor_test_semcor.bin
python resources/repositories/jex_it/jex_it.py -i $semcor_naf -t $semcor_naf -j $jex_folder -s $jex_semcor -c $jex_semcor -o $output_path

#run jex for sval2013
export output_path=$cwd/resources/feature_input/train_semcor_test_sval2013.bin
python resources/repositories/jex_it/jex_it.py -i $semcor_naf -t $sval2013_naf -j $jex_folder -s $jex_semcor -c $jex_sval2013 -o $output_path

#run jex for sval2015
export output_path=$cwd/resources/feature_input/train_semcor_test_sval2015.bin
python resources/repositories/jex_it/jex_it.py -i $semcor_naf -t $sval2015_naf -j $jex_folder -s $jex_semcor -c $jex_sval2015 -o $output_path

