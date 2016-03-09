#!/bin/bash

echo 'STARTING' `date`

for file in brown*/*.naf
do
echo "Running $file"
cat $file | /home/izquierdo/ehu_vm/EHU-ukb/run.sh > $file.ukb 2> $file.err
n=`wc -l $file.ukb | cut -d' ' -f1`
echo "  Done with $nlines"
done

echo 'ALL DONE' `date`
