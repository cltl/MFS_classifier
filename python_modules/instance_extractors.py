from my_utilities import * 
import sys
import os
from nltk.corpus import wordnet as wn
import cPickle


def instance_extractor_semcor16(kaf_naf_obj, arguments):
    for term in kaf_naf_obj.get_terms():
        is_mfs = None
        for ext_ref in term.get_external_references():
            if ext_ref.get_reftype() == 'sense_number':
                if ext_ref.get_reference() == '1':
                    is_mfs = 1
                else:
                    is_mfs = 0
                break
        if is_mfs is not None:
            yield term.get_id(), is_mfs
            
            
def instance_extractor_semeval2013(kaf_naf_obj,arguments):
    for term in kaf_naf_obj.get_terms():
        is_mfs = None
        for ext_ref in term.get_external_references():
            if ext_ref.get_reftype() == 'sense' and ext_ref.get_resource()=='WordNet-3.0':
                this_lex_key = ext_ref.get_reference()
                position_percent = this_lex_key.find('%')
                lemma = this_lex_key[:position_percent]
                pos = this_lex_key[position_percent+1]
                if 'my_cache' not in arguments:
                    arguments['my_cache'] = {}
                    
                if (lemma,pos) in arguments['my_cache']:
                    sense_data_list  = arguments['my_cache'][(lemma,pos)]
                else:
                    sense_data_list = get_senses_for_lemma_pos(lemma,pos,arguments['path_to_wn_index'])
                    arguments['my_cache'][(lemma,pos)]= sense_data_list
                
                #Sense datalist is a list of senses for the lemma,pos with this info (lexkey,synset,sensenumber,freq)
                mfs_for_lemma = None
                for lexkey, synset, sense,freq in sense_data_list:
                    if sense == '1':
                        mfs_for_lemma = lexkey
                        break
                
                if this_lex_key == mfs_for_lemma:
                    is_mfs = 1
                else:
                    is_mfs = 0
                break
        if is_mfs is not None:
            yield term.get_id(), is_mfs
            
                
                
def instance_extractor_semeval2015(kaf_naf_obj,arguments):
    
    #load mfs dict (or create non-existing)
    path_mfs_data = arguments['path_to_wn_index']+".bin"
    if os.path.exists(path_mfs_data):
        mfs_data = cPickle.load(open(path_mfs_data))
    else:
        mfs_data = get_mfs_info_from_indexsense(arguments['path_to_wn_index'])
        cPickle.dump(mfs_data,open(path_mfs_data,"w"))
    
    from lxml import etree

    #loop terms to extract mfs info 
    for term in kaf_naf_obj.get_terms():
        
        is_mfs = None
        pos    = term.get_pos().lower()
        if pos == "j":
            pos = "a"
        lemma  = get_lemma(term)

        if pos == "x":
            continue
        
        for ext_ref in term.get_node().iterfind("externalReferences/externalRef"):
            
            if ext_ref.get('resource') == "semeval":
                
                identifier  = ext_ref.get('reference')
                if identifier not in arguments['official_identifiers']:
                    #print "%s in naf, but not in offical competition" % identifier
                    continue
                
                if arguments['official_identifiers'][identifier]['mw']:
                    continue
       
                gold_keys = arguments['official_identifiers'][identifier]['gold_keys']

                #if not gold_keys:
                #    print "no gold keys for %s" % identifier
                
                try:
                    mfs_key = mfs_data[lemma][pos]['mfs_key']
                except KeyError:
                    #print
                    #print "no mfs data for lemma: {lemma}".format(**locals())
                    #print "gold keys are: %s" % gold_keys
                    continue
                
                is_mfs = 0
                if mfs_key in gold_keys:
                    is_mfs = 1

                if is_mfs is not None:
                    #print 'succes',term.get_id(),term.get_lemma()
                    #print lemma,pos
                    #print is_mfs,mfs_key,gold_keys
                    #raw_input('continue?')
                    yield term.get_id(), is_mfs
                #else:
                #    print 'failure',term.get_id(),term.get_lemma()
                #    print lemma,pos
                #    print is_mfs,mfs_key,gold_keys
                #    raw_input('continue?')
