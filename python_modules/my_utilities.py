from subprocess import check_output
import subprocess
from math import log
import sys
from collections import defaultdict

from supersense_list import SS as SS_mapping
from nltk.corpus import wordnet as wn
import nltk 

def normalyse_pos(pos):
    normalised_pos = None ##[a,n,r,v]$
    pos = (pos[0]).lower()
    if pos in ['1','n']:
        normalised_pos = 'n'
    elif pos in ['2','v']:
        normalised_pos = 'v'
    elif pos in ['3','5','j']:
        normalised_pos = 'a'
    elif pos in ['4','r']:
        normalised_pos = 'r'
    else:
        normalised_pos = pos
    return normalised_pos



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


def get_mfs_for_lemma_pos(lemma,pos,path_to_index_sense):
    if pos == 'n':      pos = '1'
    elif pos == 'v':    pos = '2'
    elif pos == 'a':    pos = '[35]'
    elif pos == 'r':    pos = '4'
    elif pos == '3':    pos = '[35]'
    elif pos == '5':    pos = '[35]'
    
    cmd = 'grep "^%s%%%s" %s | grep " 1 " | cut -d" " -f1' % (lemma,pos,path_to_index_sense)
    try:
        mfs = check_output(cmd, shell=True)
        mfs = mfs.strip()
    except subprocess.CalledProcessError:
        mfs = None
    return mfs
    
def get_senses_for_lemma_pos(lemma,pos,path_to_index_sense):
    if pos == 'n':      pos = '1'
    elif pos == 'v':    pos = '2'
    elif pos == 'a':    pos = '[35]'
    elif pos == 'r':    pos = '4'
    elif pos == '3':    pos = '[35]'
    elif pos == '5':    pos = '[35]'
    
    output = ""
    try: 
        cmd = 'grep "^%s%%%s" %s' % (lemma,pos,path_to_index_sense)
        output = check_output(cmd, shell=True)
    except subprocess.CalledProcessError:
        sys.stderr.write("error processing command: %s\n" % cmd)
    data = []
    for line in output.splitlines():
        #style%1:07:00:: 04249815 2 274
        fields = line.split()
        data.append(fields)
    return data


def entropy(list_of_floats, normalized=False,base=2):
    '''
    given a list of floats, the entropy is returned
    
    >>> entropy([0.2,0.2,0.2,0.2,0.2],normalized=True)
    1.0
    
    >>> entropy([0.2,0.2,0.2,0.2,0.2],normalized=False)
    2.321928094887362
    
    >>> entropy([])
    0.0
    
    @requires: math.log 
    
    @type  list_of_floats: list
    @param list_of_floats: list of floats. for example [0.5,0.5]
    
    @type  normalized: bool
    @param normalized: if True, entropy is normalized from 0 to 1 (default
    is False)
    
    @type  base: int
    @param base: base of log (default is 2)

    @rtype: float
    @return: normalized entropy. 0.0 is returned if list is empty
    '''
    #if empty list, return 0.0:
    if not list_of_floats:
        return 0.0 
    
    #calculate Shannon Entropy (S) = -Si(piLnpi)
    S = -1.0 * sum([ (p * ( log(p,base) ) )
                  for p in list_of_floats])
    
    #normalize if needed
    if normalized:
        len_list_of_floats = len(list_of_floats)
        if len_list_of_floats > 1:
            S = S/log(len_list_of_floats,2)
    
    return S
    
def get_supersense_from_lexkey(this_lex_key):
    #lexkey = face%1:08:00::
    fields      = this_lex_key.split(':')
    ss_code     = fields[1]
    int_ss_code = int(ss_code) 
    #SS_mapping.get(ss_code,'UNK')
    return int_ss_code


def load_WND_for_synsets(path_to_file):
    WND_for_synset = {}
    fd = open(path_to_file, 'r')
    for line in fd:
        fields = line.strip().split('\t')
        synset = fields[0]
        
        #Normalising all POS for adjectives to 'a'
        if synset[-1] == 's':
            synset = synset[:-1]+'a'
        
        WND_for_synset[synset] = fields[1]
    fd.close()
    return WND_for_synset


def get_lemma(term_obj):
    lemma = term_obj.get_lemma().lower()
    lemma = lemma.replace("-","")
    lemma = lemma.replace(" ","_") 

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
    return lemma

def get_mfs_info_from_indexsense(index_sense_path):
    '''
    extract mfs info of sense keys from index.sense file
    
    @type  index_sense_path: str
    @param index_sense_path: full path to index.sense path of a wordnet version
    
    @rtype: dict
    @return: dict mapping from lemma ->
        --> pos (n v r a)
            'mfs_key'    -> lexkey (str)
            'num_senses' -> num_senses (int)
    '''
    mfs_data = defaultdict(dict)
    mapping = {'1':'n','2':'v', '3': 'a', '4': 'r', '5': 'a'}

    with open(index_sense_path) as infile:
        for line in infile:
            key,offset,sqr,freq = line.strip().split()
            lemma,identifier    = key.split("%")
            pos                 = mapping[identifier[0]]
           
            #add keys and mfs key
            if lemma not in mfs_data:
                mfs_data[lemma] = {}
            if pos not in mfs_data[lemma]:
                mfs_data[lemma][pos] = {}
                mfs_data[lemma][pos]['keys'] = []
            
            mfs_data[lemma][pos]['keys'].append(key)
            if sqr == "1":
                mfs_data[lemma][pos]['mfs_key'] = key
            
    #compute num_senses + remove keys
    for lemma,info in mfs_data.iteritems():
        for pos,value in info.iteritems():
            mfs_data[lemma][pos]['num_senses'] = len(value['keys'])
            del mfs_data[lemma][pos]['keys']
            
    return mfs_data

