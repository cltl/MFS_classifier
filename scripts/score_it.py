import argparse
import os 
import cPickle

#import installed or created modules
import utils
from strategy import Strategy

#parse arguments
parser = argparse.ArgumentParser(description='Score wsd performance of wsd system + mfs classifier')
    
parser.add_argument('-i', dest='input_folder',     help='naf files with both wsd system + gold senses',  required=True)
parser.add_argument('-r', dest='resource',         help='resource attribute value of system in naf'   ,  required=True)
parser.add_argument('-c', dest='mfs_classifier',   help='path to pickle with output mfs_classifier',     required=True)
parser.add_argument('-e', dest='competition',      help='sval2013 | sval2015',                           required=True)
parser.add_argument('-s', dest='strategy',         help='supported: system | n | p | np',                required=True)
parser.add_argument('-k', dest='path_identifiers', help='path to .bin of competition',                   required=True)
parser.add_argument('-g', dest='gold_key',         help='gold key file of competition',                  required=True)
parser.add_argument('-f', dest='scorer',           help='scorer folder',                                 required=True)
parser.add_argument('-o', dest='output_folder',    help='folder where output will be scored',            required=True)
parser.add_argument('-w', dest='wn_index_sense',   help='full path to wordnet index.sense file',         required=True)
args = parser.parse_args()

args.official_identifiers = cPickle.load(open(args.path_identifiers))
num_instances             = len(args.official_identifiers)
args.lexkey2sense_number  = { line.strip().split()[0]: int(line.strip().split()[2])
                              for line in open(args.wn_index_sense) }

data = utils.in_a_pickle(args)

#create output based on strategy
strategy_instance = Strategy(data,args)
output = strategy_instance.output


#multi-word step
#if args.competition == "sval2015":
#    output = utils.multi_word(args,output)
#    num_instances             = len(open(args.path_identifiers).readlines())

#save pickle of output
#with open('inspection.bin','w') as outfile:
#    cPickle.dump(output,outfile)

#accuracy : based on gold senses in naf + official identifiers
r_wsd_own        = [instance['correct'] for instance in output.itervalues()].count(True) / float(num_instances)
r_wsd_own        = round(r_wsd_own,3)
num_non_mfs      = [instance['mfs'] not in instance['gold'] for instance in output.itervalues()].count(True)
num_mfs          = [instance['mfs'] in instance['gold'] for instance in output.itervalues()].count(True)
r_wsd_lfs        = [instance['correct'] for instance in output.itervalues()
                    if instance['mfs'] not in instance['gold'] ].count(True) / float(num_non_mfs)
r_wsd_lfs        = round(r_wsd_lfs,3)
accuracy_mfs     = [instance['correct'] for instance in output.itervalues()
                    if instance['mfs'] in instance['gold'] ].count(True) / float(num_mfs)
mfs_baseline     = [instance['mfs'] in instance['gold'] for instance in output.itervalues()].count(True) / float(num_instances)
mfs_baseline = round(mfs_baseline,3)

#check performance per pos

if args.strategy == 'system':
    for pos in ['a','n','v','r']:
        
        pos_instances = [instance['correct'] 
                        for instance in output.itervalues()
                        if instance['pos'] == pos]
        if pos_instances:
            r_wsd_own_pos = round( sum(pos_instances) / float(len(pos_instances)),2)
            print(pos,r_wsd_own_pos)
        
#update bin with output mfs classifier
#path_best_setting_bin = os.sep.join([args.output_folder,"best_setting.bin"])
#best_setting_bin = cPickle.load(open(path_best_setting_bin))
#num_mfs_classifier = [instance['mfs_classifier'] is not None for instance in output.itervalues()].count(True)
#num_instances = float( len(open(args.gold_key).readlines()) )
#perc_of_instances = num_mfs_classifier / num_instances 
#best_setting_bin['perc_of_instances'] = perc_of_instances
#with open(path_best_setting_bin,"w") as outfile:
#       cPickle.dump(best_setting_bin,outfile)

##convert output to semeval input
path_input_semeval = os.sep.join([args.output_folder,"input_semeval.txt"])

utils.create_input_semeval(args,output,path_input_semeval)

#precision,recall according to offical scorer
p_wsd,r_wsd      = utils.score_it(args.scorer,path_input_semeval,args.gold_key,args.competition)
analysis         = utils.analyse(output)

#add to general csv with strategy as variable
results_csv   = os.sep.join([args.output_folder,"results.csv"])
extra_headers = ['Pbin','Rbin','ACCbin','TN_rate','TP','FP','TN','FN']

if os.path.exists(results_csv) == False:
    with open(results_csv,"w") as outfile:
        headers       = ["strategy","Pwsd","Rwsd","Rwsd_own","Rwsd_lfs",'MFSbaseline','2nd_sense'] 
        outfile.write("\t".join(headers + extra_headers)+"\n")

with open(results_csv,"a") as outfile:
    general_stuff = [args.strategy,p_wsd,r_wsd,str(r_wsd_own),str(r_wsd_lfs),str(mfs_baseline),str(strategy_instance.n_performance)]
    extra_stuff   = [str(analysis[item]) for item in extra_headers]
    outfile.write("\t".join(general_stuff + extra_stuff)+"\n")

#save sense distribution
if args.strategy == 'system':
    path = os.path.join(args.output_folder,'sense_distribution_system.bin')
    with open(path,'w') as outfile:
        cPickle.dump(strategy_instance.sense_distribution,outfile)
