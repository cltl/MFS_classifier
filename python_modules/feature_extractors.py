from my_utilities import * 
from nltk.corpus import wordnet as wn
from scipy.stats import spearmanr
from scipy.stats.stats import pearsonr   
from numpy import array 
import sys
import math

def get_supersense_for_mfs(kaf_naf_obj, term_id, arguments):
    '''
    Obtains the supersense associated with the MFS for the term (the sense number #1 for the lemma in WN3.0)
    '''
    
    term_obj = kaf_naf_obj.get_term(term_id)
    lemma = get_lemma(term_obj)
    pos = normalyse_pos(term_obj.get_pos())
    sense_data_list = None
    if (lemma,pos) in arguments['cache_senses_wn30']:
        sense_data_list = arguments['cache_senses_wn30'][(lemma,pos)] 
    else:
        sense_data_list = get_senses_for_lemma_pos(lemma,pos,arguments['path_to_index_sense'])
        arguments['cache_senses_wn30'][(lemma,pos)] = sense_data_list
        
    ## sense_data_list is a list of tuples like this:
    #  ['person%1:03:00::', '00007846', '1', '6833']  (lexkey, synset, sense_number, frequency in WN)
    
    lex_key_for_mfs = None
    for lexkey, synset, sense_number, freq in sense_data_list:
        if sense_number == '1':
            lex_key_for_mfs = lexkey
            break
        
    if lex_key_for_mfs is not None:
        supersense_for_mfs = get_supersense_from_lexkey(lex_key_for_mfs)
    else:
        supersense_for_mfs = 45
    
    yield str(supersense_for_mfs)


def get_WND_for_mfs(kaf_naf_obj, term_id, arguments):
    '''
    Obtains the WND associated with the MFS for the term (the sense number #1 for the lemma in WN3.0)
    '''
    term_obj = kaf_naf_obj.get_term(term_id)
    lemma = get_lemma(term_obj)
    pos = normalyse_pos(term_obj.get_pos())
    sense_data_list = None
    if (lemma,pos) in arguments['cache_senses_wn20']:
        sense_data_list = arguments['cache_senses_wn20'][(lemma,pos)] 
    else:
        sense_data_list = get_senses_for_lemma_pos(lemma,pos,arguments['path_to_index_sense_wn20'])
        arguments['cache_senses_wn20'][(lemma,pos)] = sense_data_list
        
    synset_for_mfs = None
    for lexkey, synset, sense_number, freq in sense_data_list:
        if sense_number == '1':
            synset_for_mfs = synset
            break
        
    if len(arguments['WND_for_synset']) == 0:
        arguments['WND_for_synset'] = load_WND_for_synsets(arguments['WND_file'])
    
    WND_label = 'UNK'
    if synset_for_mfs is not None:
        synset_pos = synset_for_mfs+'-'+pos
        WND_label = arguments['WND_for_synset'].get(synset_pos,'UNK')
    #print lemma,pos,sense_data_list, WND_label

    int_domain = sum([ord(character) for character in WND_label])
    yield str(int_domain)


def ratio_WND(kaf_naf_obj, term_id, arguments):
    '''
    Obtains the ratio of WND labels associated with the word
    '''
    term_obj = kaf_naf_obj.get_term(term_id)
    lemma = get_lemma(term_obj)
    pos = normalyse_pos(term_obj.get_pos())
    sense_data_list = None
    if (lemma,pos) in arguments['cache_senses_wn20']:
        sense_data_list = arguments['cache_senses_wn20'][(lemma,pos)] 
    else:
        sense_data_list = get_senses_for_lemma_pos(lemma,pos,arguments['path_to_index_sense_wn20'])
        arguments['cache_senses_wn20'][(lemma,pos)] = sense_data_list  
        
    if len(arguments['WND_for_synset']) == 0:
        arguments['WND_for_synset'] = load_WND_for_synsets(arguments['WND_file'])
    
    ratio = 0
    if len(sense_data_list) > 0:    
       # print lemma, pos
        number_factotum = 0
        for lexkey, synset, sense_number, freq in sense_data_list:
            synset_pos = synset+'-'+pos
            WND_label = arguments['WND_for_synset'].get(synset_pos,'UNK')
            if WND_label == 'factotum':
                number_factotum += 1
            #print '\t', synset, WND_label, len(arguments['WND_for_synset'])
        #print 'Total senses %d, total factotum %d' % (len(sense_data_list), number_factotum)
        ratio = number_factotum*100.0/len(sense_data_list)
        #print 'RATIO: %f' % ratio
    
    yield '%.2f' % ratio

def get_confidence_mfs_ofims(kaf_naf_obj, term_id, arguments):
    confidence_mfs = 0.0

    term_obj = kaf_naf_obj.get_term(term_id)
    lemma    = term_obj.get_lemma()
    [pos      for pos in get_pos(kaf_naf_obj, term_id,{'to_int':False} )]
    
    lemma_pos_number = "{lemma}.{pos}.1".format(**locals())
    mfs              = convert_lemma_pos_number_to_ilidef(wn,'30',lemma_pos_number)
    
    for ext_ref in term_obj.get_external_references():
        if ext_ref.get_resource() == 'WordNet-3.0#IMS_original_models':    
            reference = ext_ref.get_reference()
            if reference == mfs:
                confidence_mfs = ext_ref.get_confidence()

    yield str(confidence_mfs)
            

def get_confidence_mfs_of_ims171(kaf_naf_obj, term_id, arguments):
    term_obj = kaf_naf_obj.get_term(term_id)
    confidence_for_sense = {}
    for ext_ref in term_obj.get_external_references():
        if ext_ref.get_resource() == 'WordNet-3.0#IMS_original_models':
            confidence_for_sense[ext_ref.get_reference()] = ext_ref.get_confidence()

    ims_confidence_for_mfs = '0'
    if len(confidence_for_sense) != 0: #Example br-c02.naf, t81 has no IMS annotations, lemma is group but token is NBC
        
        #Calculate what is the MFS for this case
        # Get one random key
        one_key = confidence_for_sense.keys()[0]
        position_percent = one_key.find('%')
        lemma = one_key[:position_percent]
        pos = one_key[position_percent+1]
        if (lemma,pos) in arguments['my_cache']:
            sense_data_list = arguments['my_cache'][(lemma,pos)] 
        else:
            sense_data_list = get_senses_for_lemma_pos(lemma,pos,arguments['path_to_index_sense'])
            arguments['my_cache'][(lemma,pos)] = sense_data_list
        
        #Sense datalist is a list of senses for the lemma,pos with this info (lexkey,synset,sensenumber,freq)
        mfs_for_lemma = None
        for lexkey, synset, sense,freq in sense_data_list:
            if sense == '1':
                mfs_for_lemma = lexkey
                break
        ims_confidence_for_mfs = confidence_for_sense.get(mfs_for_lemma,'0')
    yield ims_confidence_for_mfs
    
def get_entropy_sense_ranking_ims171(kaf_naf_obj, term_id, arguments):
    term_obj = kaf_naf_obj.get_term(term_id)
    list_of_confidences = []
    for ext_ref in term_obj.get_external_references():
        if ext_ref.get_resource() == 'WordNet-3.0#IMS_original_models':
            conf = float(ext_ref.get_confidence())
            if conf != 0.0:
                list_of_confidences.append(conf)    
    this_entropy = entropy(list_of_confidences,normalized=True)
    yield str(this_entropy)

def get_idf(kaf_naf_obj, term_id, arguments):
    idf = 0.0
    term_obj = kaf_naf_obj.get_term(term_id) 
    lemma    = term_obj.get_lemma()   
    
    if lemma in arguments['dict']:
        idf = arguments['dict'][lemma]

    yield str(idf)

def get_jex(kaf_naf_obj, term_id, arguments):
    yield 'yes'

def get_confidence_mfs_of_ukb30(kaf_naf_obj, term_id, arguments):
    term_obj = kaf_naf_obj.get_term(term_id)
    confidence_for_sense = {}
    for ext_ref in term_obj.get_external_references():
        if ext_ref.get_resource() == 'wn30g.bin64':
            confidence_for_sense[ext_ref.get_reference()] = ext_ref.get_confidence()
            
    ukb_confidence_for_sense = '0'
    if len(confidence_for_sense) !=0:
        one_ili = confidence_for_sense.keys()[0] 
        lemma = get_lemma(term_obj)
        pos = one_ili[-1]   #a n v r
        if (lemma,pos) in arguments['my_cache_wn30']:
            sense_data_list = arguments['my_cache_wn30'][(lemma,pos)]
        else:
            sense_data_list = get_senses_for_lemma_pos(lemma,pos,arguments['path_to_index_sense'])
            arguments['my_cache_wn30'][(lemma,pos)]= sense_data_list
        
        #Sense datalist is a list of senses for the lemma,pos with this info (lexkey,synset,sensenumber,freq)
        ili_mfs_for_lemma = None
        for lexkey, synset, sense,freq in sense_data_list:
            if sense == '1':
                ili_mfs_for_lemma = synset
                break
        ili_mfs_for_lemma = 'ili-30-%s-%s' % (ili_mfs_for_lemma,pos)
        ukb_confidence_for_sense = confidence_for_sense.get(ili_mfs_for_lemma,'0.0')
    
    yield '%.10f' % float(ukb_confidence_for_sense)
    

def get_entropy_sense_ranking_ukb30(kaf_naf_obj, term_id, arguments):
    term_obj = kaf_naf_obj.get_term(term_id)
    list_of_confidences = []
    for ext_ref in term_obj.get_external_references():
        if ext_ref.get_resource() == 'wn30g.bin64':
            conf = float(ext_ref.get_confidence())
            if conf != 0.0:
                list_of_confidences.append(conf)    
    this_entropy = entropy(list_of_confidences,normalized=True)
    yield str(this_entropy)

def correlation_confidences_semcor_and_system(kaf_naf_obj,term_id,arguments):
    '''
    return pearson correlation between senses confidences of UKB and semcor
    '''
    #check if object comes from semcor -> reutrn 1.0
    #if kaf_naf_obj.filename.startswith('br-'):
    #    yield str(1.0)

    #set default value
    correlation = str(0.0)

    #obtain senses + frequencies from semcor, else return 0.0
    term_obj         = kaf_naf_obj.get_term(term_id)
    lemma            = term_obj.get_lemma()
    pos              = term_obj.get_pos()[0].lower()
    if (lemma,pos) in arguments['dict']:
        senses = arguments['dict'][(lemma,pos)]['senses']
        if not senses:
            correlation = str(0.0)
        total = sum(senses.values())
        semcor = { key.replace('eng','ili-'): (float(value)/total) for key,value in senses.iteritems()}
        correlation = 'default'
    else:
        correlation = str(0.0)

    #obtain senses from system
    system = {}
    for ext_ref in term_obj.get_external_references():
        if ext_ref.get_resource() == arguments['resource']:
            conf = float(ext_ref.get_confidence())
            if conf != 0.0:
                reference = ext_ref.get_reference()
                system[reference] = conf

    #calculate correlation 
    if correlation == 'default':
        v1 = []
        v2 = []
        
        for key,value in system.iteritems():
            v1.append(round(value,2))
            if key in semcor:
                v2.append(round(semcor[key],2))
            else:
                v2.append(0.0)

        correlation,p_value = pearsonr(array(v1),array(v2))  
        if math.isnan(correlation):
            correlation = str(0.0)   
    yield str(correlation)

def get_number_of_senses(kaf_naf_obj, term_id, arguments):
    term_obj = kaf_naf_obj.get_term(term_id)
    num_senses = 0
    for ext_ref in term_obj.get_external_references():
        if ext_ref.get_resource() == 'wn30g.bin64': #now based on ukb
            num_senses += 1
    yield str(num_senses)

def get_number_of_senses_wordnet(kaf_naf_obj, term_id, arguments):
    term_obj = kaf_naf_obj.get_term(term_id)
    lemma    = term_obj.get_lemma()
    [pos      for pos in get_pos(kaf_naf_obj, term_id,{'to_int':False} )]
    
    if (lemma,pos) in arguments['num_senses']:
        num_senses = arguments['num_senses'][(lemma,pos)]
    else: 
        num_senses = len(wn.synsets(lemma,pos=pos))
        arguments['num_senses'][(lemma,pos)] = num_senses
    return str(num_senses)

def get_sense_entropy(kaf_naf_obj, term_id, arguments):
    term_obj         = kaf_naf_obj.get_term(term_id)
    lemma            = term_obj.get_lemma()
    pos              = term_obj.get_pos()[0].lower()
    if (lemma,pos) in arguments['dict']:
        S = arguments['dict'][(lemma,pos)]['entropy']
    else:
        S =0.0    
    
    yield str(S)

def get_pos(kaf_naf_obj, term_id, arguments):
    term_obj         = kaf_naf_obj.get_term(term_id)
    pos              = term_obj.get_pos()
    first_letter_pos = pos[0]
    mapping          = {'N' : 1,
                        'V' : 2,
                        'A' : 3,
                        'J' : 3,
                        'R' : 4}
    if arguments['to_int']:
        pos = mapping[first_letter_pos]
        yield str(pos)
    else:
        if first_letter_pos == "J":
            first_letter_pos = "A"
        yield first_letter_pos.lower()
    
                        
def get_bow_tokens(kaf_naf_obj,term_id, arguments):
    idx_for_token_id = {}
    if hasattr(kaf_naf_obj, 'token_data'):
        token_data = kaf_naf_obj.token_data
        idx_for_token_id = kaf_naf_obj.idx_for_token_id
        token_id_for_term_id = kaf_naf_obj.token_id_for_term_id
    else:
        idx_for_token_id = {}
        token_data = []
        for token in kaf_naf_obj.get_tokens():
            idx_for_token_id[token.get_id()] = len(token_data)
            token_data.append((token.get_id(),token.get_text(),token.get_sent()))
    
        token_id_for_term_id = {}
        for term in kaf_naf_obj.get_terms():
            for span_id in term.get_span().get_span_ids():
                token_id_for_term_id[term.get_id()] = span_id
                
        kaf_naf_obj.token_data = token_data
        kaf_naf_obj.idx_for_token_id = idx_for_token_id
        kaf_naf_obj.token_id_for_term_id = token_id_for_term_id
        
                         
    this_token_id = token_id_for_term_id[term_id]
    this_index = idx_for_token_id[this_token_id]
    size_context = arguments.get('token_window',3)    #default 3
    start_index = max(0,this_index-size_context)
    end_index = min(len(token_data)-1,this_index+size_context)
            
    for current_idx in xrange(start_index,end_index+1):
        token_id, text, sent = token_data[current_idx]
        feature = 'bow#%s' % text
        yield feature
        

def get_positional_tokens(kaf_naf_obj,term_id, arguments):
    if hasattr(kaf_naf_obj, 'token_data'):
        token_data = kaf_naf_obj.token_data
        idx_for_token_id = kaf_naf_obj.idx_for_token_id
        token_id_for_term_id = kaf_naf_obj.token_id_for_term_id
    else:
        idx_for_token_id = {}
        token_data = []
        for token in kaf_naf_obj.get_tokens():
            idx_for_token_id[token.get_id()] = len(token_data)
            token_data.append((token.get_id(),token.get_text(),token.get_sent()))
    
        token_id_for_term_id = {}
        for term in kaf_naf_obj.get_terms():
            for span_id in term.get_span().get_span_ids():
                token_id_for_term_id[term.get_id()] = span_id
                
        kaf_naf_obj.token_data = token_data
        kaf_naf_obj.idx_for_token_id = idx_for_token_id
        kaf_naf_obj.token_id_for_term_id = token_id_for_term_id
        
                         
    this_token_id = token_id_for_term_id[term_id]
    this_index = idx_for_token_id[this_token_id]
    size_context = arguments.get('token_window',3)    #default 3
    start_index = max(0,this_index-size_context)
    end_index = min(len(token_data)-1,this_index+size_context)
    
    for current_idx in xrange(start_index,end_index+1):
        position = current_idx - this_index
        token_id, text, sent = token_data[current_idx]
        feature = 'token#%d#%s' % (position,text)
        yield feature        
