
#paths and variables
export cwd=/${PWD#*/}
input_dir=$cwd/resources/extracted_features
output_dir=$cwd/output
wsd_corpora=$cwd/resources/wsd_corpora
wn_index_sense=$cwd/resources/wordnets/WordNet-3.0/dict/index.sense

mkdir -p $output_dir

for competition in "sval2013.csv" "sval2015.csv";

do
    
    if [ "$competition" = "sval2013.csv" ];
    then
        input_folder=$wsd_corpora/semeval2013_task12/en
        the_competition="sval2013"
        identifiers=$cwd/resources/identifiers/sval2013.bin
        scorer=$cwd/resources/scorers/semeval-2013-task12-test-data/scorer
        gold_key=$cwd/resources/scorers/semeval-2013-task12-test-data/keys/gold/wordnet/wordnet.en.key.nomw
    fi 

    if [ "$competition" = "sval2015.csv" ];
    then
        input_folder=$wsd_corpora/semeval2015_task13_en
        the_competition="sval2015"
        identifiers=$cwd/resources/identifiers/sval2015.bin
        scorer=$cwd/resources/scorers/SemEval-2015-task-13-v1.0/scorer
        gold_key=$cwd/resources/scorers/SemEval-2015-task-13-v1.0/keys/gold_keys/EN/semeval-2015-task-13-en.key.nomw
    fi

    for system in "UKB" "IMS";

    do
        if [ "$system" = "UKB" ]
        then
            resource="wn30g.bin64"
        fi

        if [ "$system" = "IMS" ]
        then
            resource="WordNet-3.0#IMS_original_models"
        fi
       

        #dev part
                

 
        if [ "$competition" = "sval2013.csv" ]
        then
            export test=$input_dir/sval2015.csv
        fi
 
        if [ "$competition" = "sval2015.csv" ]
        then
            export test=$input_dir/sval2013.csv
        fi

        #test part
        export train=$input_dir/semcor.csv
        export test=$input_dir/$competition
        export results=$test.$system.csv
        export out=$output_dir/$competition-$system
        export label="accuracy" 
        mkdir -p $out 
        rm -rf $out/results.csv
        rm -rf $out/best_setting.txt
        mfs_classifier=$(python scripts/scoring_prep.py -i $train -t $test -o $out -r $results -l $label)
        for strategy in 'gold_classifier' 'system' 'n' 'p' 'np';
        do
            python scripts/score_it.py -i $input_folder -r $resource -c $mfs_classifier -e $the_competition -s $strategy -k $identifiers -g $gold_key -f $scorer -o $out -w $wn_index_sense
        done
        echo
        echo $competition $system $label
        cat $out/results.csv
        cat $results.ablation.csv
        #cat $out/best_setting.txt
        #cat $out/performance_n_per_pos.txt
        #python scripts/plot_it.py -i $out/results.csv -t $competition-$system -o $out/results.pdf
    done
done



