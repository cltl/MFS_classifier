import os
import sys
import glob
import cPickle
from collections import defaultdict
import subprocess 
import re

#import installed or created modules
#from nltk.corpus import wordnet as wn
#import nltk
from lxml import etree

def convert_lemma_pos_number_to_ilidef(wn,version,lemma_pos_number):
    '''
    given a lemma_pos_number, this method convert it to an ilidef
    
    @type  wn: nltk.corpus.util.LazyCorpusLoader
    @param wn: wordnet loaded into memory

    @type  version: str
    @param version: version of wordnet: 30 

    @lemma_pos_number: str
    @lemma_pos_number: for example 'house.n.1'
    '''
    try:
        synset = wn.synset(lemma_pos_number)
    except nltk.corpus.reader.wordnet.WordNetError:
        return ""
    

    pos           = lemma_pos_number.split('.')[1]
    offset        = str(synset.offset)
    length_offset = len(offset)
    zeros         = (8-length_offset)*'0'
    ilidef        = "ili-{version}-{zeros}{offset}-{pos}".format(**locals())
    
    return ilidef

def in_a_pickle(args):
    '''
    given the arguments in args (argparse namespace)
    the naf files are stored in one defaultdict
    '''
    #load mfs dict
    path_bin = args.wn_index_sense+".bin"
    if os.path.exists(path_bin) == False:
        mfs_data = get_mfs_info_from_indexsense(args.wn_index_sense)
        cPickle.dump(mfs_data,open(path_bin,"w"))
    else:
        mfs_data = cPickle.load(open(path_bin))

    #set dict
    data        = defaultdict(dict)
    
    #previous lemma
    prev_lemma = "dummy"
    prev_iden  = ""
 
    # load mfs classifier output dict
    mfs_classifier_output,evaluation = cPickle.load(open(args.mfs_classifier))
    
    #loop over naf files
    for naf_file in glob.glob("{input_folder}/*.naf".format(input_folder=args.input_folder)):
        
        #parse naf file
        basename            = os.path.basename(naf_file)
        doc                 = etree.parse(naf_file)
        
        #loop over term elements
        if args.competition == "sval2013":
            path_identifier = "terms/term/externalReferences/externalRef[@reftype='original_id']"
        elif args.competition == "sval2015":
            path_identifier = "terms/term/externalReferences/externalRef[@resource='semeval']"
        
        for ext_ref_el in doc.iterfind(path_identifier):
            identifier = ext_ref_el.get('reference')
            if identifier not in args.official_identifiers:
                continue
            gold       = args.official_identifiers[identifier]['gold_keys']
            
            ext_refs_el = ext_ref_el.getparent()
            term_el     = ext_refs_el.getparent()
            
            #extra basic information about term
            term_id    = term_el.get("id")
            whole_id   = "---".join([naf_file,term_id])
            pos        = get_pos(args,term_el)
            lemma      = get_lemma(args,term_el)
            polysemy   = 0
            mfs        = ""
            if lemma in mfs_data:
                polysemy = mfs_data[lemma][pos]['num_senses'] 
                mfs      = mfs_data[lemma][pos]['mfs_key']
            else:
                sys.stderr.write(lemma + " not in mfs_data\n")
    
            #get output system on this term 
            system_all  = [( float(el.get('confidence')),el.get('reference') )
                           for el in term_el.iterfind('''externalReferences/externalRef[@resource="%s"]''' % args.resource)]
            system_all  = sorted(system_all,reverse=True)

            system      = ""
            if system_all:
                confidence,system = system_all[0]
                
            #obtain result mfs classifier
            if whole_id in mfs_classifier_output:
                mfs_classifier = mfs_classifier_output[whole_id]
            else:
                mfs_classifier = None

            #update dict
            if identifier in args.official_identifiers:
                data[identifier] =     {'mfs_classifier' : mfs_classifier,
                                        'mfs'            : mfs,
                                        'identifier'     : identifier,
                                        'identifier2'    : identifier,
                                        'system'         : system,
                                        'system_all'     : system_all,
                                        'gold'           : gold,
                                        'lemma'          : lemma,
                                        'pos'            : pos,
                                        'monosemous'     : polysemy == 1,
                                        'polysemy'       : polysemy,
                                        'prev_lemma'     : prev_lemma,
                                        'prev_iden'      : prev_iden}
            
            prev_lemma = lemma
            prev_iden  = identifier
    return data

def create_input_semeval(args,output,path_input_semeval):
    '''
    given the output dict from the strategy and the input path to semeval
    the input for semeval is created
    '''
    with open(path_input_semeval,"w") as outfile:
        for identifier in args.official_identifiers:
            
            info    = output[identifier]
            if info['lexkey']:
                if args.competition == "sval2013":
                    outline = "{doc} {identifier} {lexkey} !! lemma={lemma}#{pos}".format(**info)
                elif args.competition == "sval2015":
                    outline = "{identifier}\t{identifier2}\twn:{lexkey}".format(**info)
                outfile.write(outline+"\n")
            else:
                sys.stderr.write('no answer for %s\n' % info['identifier'])
                sys.stderr.write(str(info)+'\n')

def score_it(scorer_folder,system_path,key_file,competition):
    '''
    given the scorer folder,system_path and key_file, the precision and recall is returned
    
    @type  scorer_folder: str
    @param scorer_folder: full path to scorer folder of sval scorer
    
    @type  system_path: str
    @param system_path: full path to sval system submission
    
    @type  key_file: str
    @param key_file: full path to gold standard sval competition
    
    @type  competition: str
    @param competition: sval2013 | sval2015
    
    @rtype: tuple
    @return: (precision,recall) both as strings    
    '''
    #create custom call based on competition
    if competition == "sval2013":
        call = "perl score.pl {system_path} {key_file}".format(**locals())
    if competition == "sval2015":
        call = "java Scorer {key_file} {system_path}".format(**locals())
    
    #set command
    command = "cd {scorer_folder} && {call}".format(**locals())
    
    #call scorer
    evaluation_output = subprocess.check_output(command,shell=True)

    #extract precision and recall from output
    if competition == "sval2013":
        precision = re.findall("precision: (.*) \(",evaluation_output)[0]
        recall    = re.findall("recall: (.*) \(",evaluation_output)[0]
    
    elif competition == "sval2015":
        precision = re.findall("P=\t(.*)%",evaluation_output)[0]
        recall    = re.findall("R=\t(.*)%",evaluation_output)[0]
        precision = str(float(precision)/100)
        recall    = str(float(recall)/100)
    
    return precision,recall

def get_pos(args,term_el):
    '''
    @type  args: namespace
    @param args: namespace of command line arguments

    @type  term_el: lxml.etree._Element
    @param term_el: 'term' element in xml

    @rtype: str
    @return: n | v | r | a
    '''
    if args.competition == "sval2013":
        return "n"
    elif args.competition == "sval2015":
        #set(['X', 'J', 'V', 'R', 'N']) in naf
        pos = term_el.get('pos').lower()
        if pos == "j":
            pos = "a"
        return pos
 
def get_lemma(args,term_el):
    '''
    @type  args: namespace
    @param args: namespace of command line arguments

    @type  term_el: lxml.etree._Element
    @param term_el: 'term' element in xml

    @rtype: str
    @return: lemma 
    ''' 
    lemma = term_el.get('lemma')
    if args.competition == "sval2013":
        return lemma.lower()
    elif args.competition == "sval2015":
        if lemma == "?":
            return "question_mark"
        elif lemma == "ctrl":
            return "control_key"
        elif lemma == "f(x)":
            return "mathematical_function"
        elif lemma == "vicepresident":
            return "vice_president"
        elif lemma == "antimetabolites":
            return "antimetabolite"
        else:
            return lemma


def analyse(output):
    '''
    output dict is analysed in terms of tp,fp,tn,fp,tn_rate,fp_rate
    '''
    TP=0.0
    FP=0.0
    TN=0.0
    FN=0.0
    
    for identifier,info in output.iteritems():
        
        g = info['mfs'] in info['gold']
        s = info['lexkey'] == info['mfs']
        
        if g:
            g=1
        else:
            g=0
        if s:
            s=1 
        else:
            s=0
        
        values = [g,s]
        
        if values == [0,0]:
            TN +=1
        elif values == [1,1]:
            TP +=1
        elif values == [1,0]:
            FN +=1
        elif values == [0,1]:
            FP +=1
        
    Pbin =  TP / (FP+TP)
        
    Rbin =  TP / (TP+FN)
        
    #accuracy
    ACCbin = (TP + TN) / (TP + TN + FP + FN) 
    TN_rate = TN/(FP+TN)
    return                     {'TN_rate'       : round(TN_rate,3),
                                'Pbin'          : round(Pbin,3),
                                'Rbin'          : round(Rbin,3),
                                'ACCbin'        : round(ACCbin,3),
                                'FP'            : FP,
                                'FN'            : FN,
                                'TP'            : TP,
                                'TN'            : TN}



def get_mfs_info_from_indexsense(index_sense_path):
    '''
    extract mfs info of sense keys from index.sense file
    
    @type  index_sense_path: str
    @param index_sense_path: full path to index.sense path of a wordnet version
    
    @rtype: collections.defaultdict
    @return: defaultdict mapping from lemma ->
        'mfs_key'    -> lexkey (str)
        'num_senses' -> num_senses (int)
    '''
    mfs_data = defaultdict(dict)
    
    with open(index_sense_path) as infile:
        for line in infile:
            key,offset,sqr,freq = line.strip().split()
            lemma               = key.split("%")[0]
            
            #add keys and mfs key
            mfs_data[lemma].setdefault('keys',[]).append(key)
            if sqr == "1":
                mfs_data[lemma]['mfs_key'] = key
    
    #compute num_senses + remove keys
    for lemma,info in mfs_data.iteritems():
        mfs_data[lemma]['num_senses'] = len(info['keys'])
        del mfs_data[lemma]['keys']
    
    return mfs_data

def multi_word(args,output):
    '''
    following strategy is used if two sequential lemma have an entry in wordnet:
        (1) if monosemous: that sense is taken and inidividual identifiers removed
        (2) if polysemous: mfs of multiword is taken and individual token removed

    @type  args: namespace
    @param args: namespace of command line arguments
    
    @type  output: list 
    @param output: list of dicts (each dict representing properties of an instance in the dataset)
    
    @rtype: list
    @return: list of dicts now filtered on multi-words
    '''
    #load wordnet pickle
    path_bin = args.wn_index_sense + ".bin"
    wordnet  = cPickle.load(open(path_bin))

    for identifier,info in output.iteritems():
        potential_mw = "_".join([info['prev_lemma'],info['lemma']])
        
        if potential_mw in wordnet:
            mfs_data = wordnet[potential_mw]
            if len(mfs_data) == 1:
                pos = mfs_data.keys()[0]
                lexkey= mfs_data[pos]['mfs_key']

                d =  {     'correct'        : lexkey in info['gold'],
                           'lexkey'         : lexkey,
                           'ilidef'         : "",
                           'strategy'       : "mw",
                           'identifier'     : info['prev_iden'],
                           'identifier2'    : info['identifier'],
                           'doc'            : info['doc'],
                           'lemma'          : potential_mw,
                           'mfs'            : lexkey,
                           'gold'           : info['gold']
                    }
                    
                #TODO: add new identifer to args.official_identifiers
                output["mw_"+identifier] = d
                args.official_identifiers["mw_"+identifier] = {}
                print
                print potential_mw
                print d
                raw_input('continue?')
    return args,output





