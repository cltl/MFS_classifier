def extract_best_setting(path_results,label):
    '''
    extract setting with best result from csv

    @type  path_results: str
    @param path_results: full path to results (col 0: setting, col 7: accuracy)
    
    @type  label: str
    @param label: header to be used

    @rtype: tuple
    @return: (best_setting,best_acc)
    '''
    best_value   = 0.0
    best_setting = ""

    with open(path_results) as infile:
        for counter,line in enumerate(infile):
            split    = line.strip().split("\t")
            if counter == 0:
                index_label = split.index(label)    
                index_label-=2 #headers are off by two positions
                continue
            value = float(split[index_label])
            if value > best_value:
                best_setting = split[0]
                best_value   = value

    return best_setting,best_value

path_results="/home/postma/In_progress/mfs_classifier/resources/extracted_features/sval2015.csv.UKB.csv"
label="accuracy"

print extract_best_setting(path_results,label)
