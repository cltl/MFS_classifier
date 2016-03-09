
#paths and variables
export cwd=/${PWD#*/}
input_dir=$cwd/resources/extracted_features

export iden_col="ID"
export target="is_MFS"
export minimum="4"

for competition in "sval2013.csv" "sval2015.csv";
do
    for system in "UKB" "IMS";
    do
        mfs_output_dir=$cwd/output/$competition-$system/bins
        rm -rf $mfs_output_dir && mkdir $mfs_output_dir
        export train=$input_dir/semcor.csv
        export test=$input_dir/$competition
        export results=$test.$system.csv
        rm -rf $results
        python scripts/random_forest.py -i $train -t $test -r $results -u $iden_col -o $target -s $system -m $minimum -f $mfs_output_dir
    done
done



