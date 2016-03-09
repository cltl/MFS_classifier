import os 
from random_forest import random_forest
from evaluate import evaluate

cwd             = os.path.dirname(os.path.realpath(__file__))
path_train      = os.path.join(cwd,"example","semcor_mfs.csv")
path_test       = os.path.join(cwd,"example","semeval2013_mfs.csv")
general_results = os.path.join(cwd,"example",'results.csv')
delimiter       = "\t"
name_identifiers= "ID"
name_targets    = "is_MFS"

for features in [ ["MFS_confidence_UKB", "Entropy_sense_ranking_UKB","sense_entropy","pos","num_senses"],
                  ["MFS_confidence_UKB", "Entropy_sense_ranking_UKB", "sense_entropy"],
                  ["num_senses","pos"],
                  ["MFS_confidence_UKB", "pos"],
                  ["Entropy_sense_ranking_UKB","pos"]
                ]:
    
    classifier_output,evaluation = random_forest(path_train,
                                                 path_test,
                                                 name_identifiers,
                                                 name_targets,
                                                 features,
                                                 delimiter,
                                                 num_cores=4)
    
    
    #add to general results
    headers = "\t".join(['settings'] + evaluation.keys())
    values  = "\t".join(["-".join(features)] + 
                        [str(value) for value in evaluation.values()
                         if isinstance(value,float)
                         ])
    
    if not os.path.isfile(general_results):
        with open(general_results,"w") as outfile:
            outfile.write(headers+"\n")
            
            classifier_output,baseline_values = evaluate(evaluation['gold'],
                                                         [1 for item in classifier_output], 
                                                         evaluation.keys())
            baseline  = "\t".join(['baseline'] + 
                        [str(value) for value in baseline_values.values()
                         if isinstance(value,float)])
            outfile.write(baseline+"\n")
            
    with open(general_results,"a") as outfile:
        outfile.write(values+"\n")
        