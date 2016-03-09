import os 
import sys
import operator 
import itertools
import cPickle

#import random forest module
repo_folder = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'resources/repositories'))
sys.path.append(repo_folder)
from randomforest_python import random_forest
from randomforest_python import evaluate

import argparse
import cPickle

#parse arguments
parser = argparse.ArgumentParser(description='Run preparation for scorer')
    
parser.add_argument('-i', dest='train',    help='full path to train csv',     required=True)
parser.add_argument('-t', dest='test',     help='full path to test csv',      required=True)
parser.add_argument('-o', dest="output",   help='output folder best setting',   required=True)
parser.add_argument('-s', dest="setting",  help="if provided this setting will be used", default=None)
parser.add_argument('-r', dest="results",  help='if provided the best setting from this csv will be used', default=None)
parser.add_argument('-l', dest="label",    help='mandatory with -r results, label to rank systems on: accuracy | TN_rate', default=None)
args = parser.parse_args()

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
    feature_ablation = {}
    settings         = {}

    with open(path_results) as infile:
        for counter,line in enumerate(infile):
            split    = line.strip().split("\t")
            if counter == 0:
                index_label = split.index(label)    
                index_label-=2 #headers are off by two positions
                continue
            setting = split[0].split('-')
            setting = "-".join(sorted(setting))
            value   = float(split[index_label])
            settings[setting] = value

    best_setting = max(settings.iteritems(), key=operator.itemgetter(1))[0]
    best_value   = max(settings.values())
    worst_value  = min(settings.values())

    best_features     = best_setting.split('-')
    num_best_features = len(best_features)

    for features in itertools.combinations(best_features, num_best_features-1): 
        setting                   = "-".join(sorted(features))
        try:
            value                     = settings[setting]
        except KeyError:
            #rerun with setting
            classifier_output,evaluation = random_forest(args.train,
                                                         args.test,
                                                         "ID",
                                                         "is_MFS",
                                                         features,
                                                         "\t",
                                                         num_cores=4)
            value = evaluation['accuracy']
        missing_feature           = next(iter( set(best_features) - set(features)  )) 
        diff                      = best_value - value
        feature_ablation[missing_feature] = round(diff,3)
    return best_setting,best_value,worst_value,feature_ablation

#extract setting
if args.setting is not None:
    features = args.setting.split('-')
if args.results is not None:
    best_setting,best_value,worst_value,feature_ablation = extract_best_setting(args.results,args.label)
    features                                             = best_setting.split('-')

#write feature ablation analysis to file
feature_ablation_path = args.results + ".ablation.csv"
with open(feature_ablation_path,"w") as outfile:
    headers = ["feature","diff accuracy"]
    outfile.write("\t".join(headers)+"\n")
    outfile.write("%s\t%s\n" % ("best_setting",best_setting))
    outfile.write("%s\t%s\n" % ("worst_value", worst_value))
    outfile.write("%s\t%s\n" % ("best_value", best_value))
    for key,value in sorted(feature_ablation.iteritems(),
                            key=operator.itemgetter(1),
                            reverse=True): 
        outfile.write("-%s\t%s\n" % (key,value))

#write info about best setting to file
best_setting_path = os.sep.join([args.output,"best_setting.txt"])
with open(best_setting_path,"w") as outfile:
    outfile.write('''best setting and result based on {label}:\n {features} \n {best_acc}'''.format(label=args.label,
                                                                                                    features="-".join(features),
                                                                                                    best_acc=best_value))
best_setting_bin = os.sep.join([args.output,"best_setting.bin"])
with open(best_setting_bin,"w") as outfile:
    info = {'best_setting' : features,
            'best_polysemous_accuracy' : best_value,
           } 
    cPickle.dump(info,outfile)
            
#extract path random forest results
best_features = best_setting.split("-")
bin_path_best_setting = os.path.join(args.output,
                                     'bins',
                                     "-".join(sorted(best_features)))


#print output_path to stdout which will be a variable in ../score.sh
print(bin_path_best_setting)
