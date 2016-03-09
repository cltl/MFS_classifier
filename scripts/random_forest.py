import os 
import sys
import itertools
import argparse
from datetime import datetime
import cPickle

#import random forest module
repo_folder = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'resources/repositories'))
sys.path.append(repo_folder)
from randomforest_python import random_forest
from randomforest_python import evaluate

#argparse
parser = argparse.ArgumentParser(description='Run random forest on feature combinations')
parser.add_argument('-i', dest='train',    help='full path to train csv',     required=True)
parser.add_argument('-t', dest='test',     help='full path to test csv',      required=True)
parser.add_argument('-r', dest='results',  help='full path to results csv',   required=True)
parser.add_argument('-u', dest='iden_col', help='name of identifier column',  required=True)
parser.add_argument('-o', dest='target',   help='name of target column',      required=True)
parser.add_argument('-s',  dest="system",   help='IMS | UKB',                  required=True)
parser.add_argument('-m', dest='minimum',  help='minimum number of features (minimum is 2)', required=True, type=int)
parser.add_argument('-f', dest='bins_dir', help="directory where output bins from random forest are stored", required=True)
args = parser.parse_args()

def filter_features(args):
    '''
    given the namespace args from the command line arguments
    this method return a generator of the list of features to be considered
    
    @type  args: namespace
    @param args: namespace of command line arguments
    
    @rtype: generator
    @return: generator of the list of features to be considered in the analysis
    '''
    #not wanted system
    not_wanted = "IMS"
    if args.system == "IMS":
        not_wanted = "UKB"

    first_line = open(args.train).readline()
    features   = []
    for feature in first_line.strip().split("\t"):
        if all([feature.endswith(not_wanted) == False,
                feature != args.target,
                feature != args.iden_col]):
            features.append(feature)

    for L in range(args.minimum, len(features)+1):
        for subset in itertools.combinations(features, L):
            if [feature.endswith(args.system) for feature in features].count(True) >= 1:
                yield subset
                

delimiter       = "\t"

for features in filter_features(args): 
    
    print
    print datetime.now()
    print args.system,args.test
    print features    
    classifier_output,evaluation = random_forest(args.train,
                                                 args.test,
                                                 args.iden_col,
                                                 args.target,
                                                 features,
                                                 delimiter,
                                                 num_cores=4)
    
    #save bin
    bin_output_path = os.path.join(args.bins_dir,
                                   "-".join(sorted(features)))
    with open(bin_output_path,"w") as outfile:
        cPickle.dump((classifier_output,evaluation),outfile)
    
    #add to general results
    headers = "\t".join(['settings'] + evaluation.keys())
    values  = "\t".join(["-".join(features)] + 
                        [str(value) for value in evaluation.values()
                         if isinstance(value,float)
                         ])
    
    if not os.path.isfile(args.results):
        with open(args.results,"w") as outfile:
            outfile.write(headers+"\n")
            
            classifier_output,baseline_values = evaluate(evaluation['gold'],
                                                         [1 for item in classifier_output], 
                                                         evaluation.keys())
            baseline  = "\t".join(['baseline'] + 
                        [str(value) for value in baseline_values.values()
                         if isinstance(value,float)])
            outfile.write(baseline+"\n")
            
    with open(args.results,"a") as outfile:
        outfile.write(values+"\n")
        
