import subprocess
import argparse
from collections import defaultdict 
import os 
import cPickle

#import created or installed modules
import utils
from KafNafParserPy import KafNafParser
from lxml import etree 

#parse input arguments
parser = argparse.ArgumentParser(description='Run a naf corpus through jex')

parser.add_argument('-i', dest='train_folder',            help='folder with train naf',    required=True)
parser.add_argument('-t', dest="test_folder",             help="folder with test naf",     required=True)
parser.add_argument('-j', dest='jex_folder',              help='JEX folder',               required=True)
parser.add_argument('-s', dest="output_path_semcor",      help="full path to output",      required=True)
parser.add_argument('-c', dest="output_path_competition", help="full path to output",      required=True)
parser.add_argument("-o", dest="output_path",             help="overall output path",      required=True)
args = parser.parse_args()

#if needed, run jex on semcor
if os.path.exists(args.output_path_semcor) == False:
    print
    print 'running semcor'
    semcor = utils.run_jex(args.train_folder,args,lemma=True,document=True)
    with open(args.output_path_semcor,"w") as outfile:
        cPickle.dump(semcor,outfile)
else:
    semcor = cPickle.load(open(args.output_path_semcor))


#if needed, run jex on competition
if os.path.exists(args.output_path_competition) == False:
    competition = utils.run_jex(args.test_folder,args,lemma=False,document=True)
    with open(args.output_path_competition,"w") as outfile:
        cPickle.dump(competition,outfile)
else:
    competition = cPickle.load(open(args.output_path_competition))


#for every instance, compare lemma jex to document jex 
path_to_terms="terms/term"
output_dict = {} 

#args.input_folder should be changed to target corpus and then rerun everything
for naf_file in utils.path_generator(args.test_folder,".naf"):
   
    try: 
        doc      = etree.parse(naf_file)
        basename = os.path.basename(naf_file)
    except:
        continue

    for term_el in doc.iterfind(path_to_terms):
        
        #resource_tag = ext_ref_el.get("resource")
        #if all([ resource_tag.lower().startswith("semeval"),
        #         ext_ref_el.get("reference") in official_identifiers]):
        #term_el     = ext_ref_el.getparent().getparent()
        lemma       = term_el.get('lemma')
        t_id        = term_el.get('id')
        identifier  = "{naf_file}---{t_id}".format(**locals())
    
        d1          =  competition[basename]
        d2          =  semcor[lemma]

        correlation = utils.goodness_of_fit(d1,d2)
        output_dict[identifier] = correlation 

#outputdict is mapping path_document---term_id -> float
with open(args.output_path,"w") as outfile:
    cPickle.dump(output_dict,outfile)
