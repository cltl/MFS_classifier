
export cwd=/${PWD#*/}
out_dir=$cwd/output
paper_dir=$cwd/lrec2016


function wsd () {
echo
echo "% created with function $FUNCNAME from file $0"
python $cwd/scripts/wsd_table.py -i $out_dir -c 'sval2013' -o $paper_dir/wsd_2013.tex
python $cwd/scripts/wsd_table.py -i $out_dir -c 'sval2015' -o $paper_dir/wsd_2015.tex
echo 
cat $paper_dir/wsd_2013.tex
cat $paper_dir/wsd_2013.tex.mfs
echo
cat $paper_dir/wsd_2015.tex
cat $paper_dir/wsd_2015.tex.mfs

}

function mfs_classifier () {
echo
echo "% created with function $FUNCNAME from file $0"
python $cwd/scripts/mfs_classifier_table.py -i $out_dir -o $paper_dir/mfs_classifier_table.tex
cat $paper_dir/mfs_classifier_table.tex
}

mfs_classifier
wsd
