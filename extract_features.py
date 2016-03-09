#!/usr/bin/env python

import os
import sys
import glob
import time 

from collections import defaultdict
import cPickle

from python_modules import feature_extractors
from python_modules import instance_extractors
from KafNafParserPy import KafNafParser

__here__ = os.path.dirname(os.path.realpath(__file__))

class CorpusData:
    def __init__(self,my_id):
        self.id = my_id
        self.folder_list = None
        self.folder_extension = None
        self.instance_extractor_func = None
        self.arguments_instance_extractor = {}
        
    def get_id(self):
        return self.id
    
    def set_folder_list(self,this_list):
        self.folder_list = this_list
        
    def set_folder_extension(self,this_extension):
        self.folder_extension = this_extension
        
    def set_instance_extractor(self,instance_extractor_name, arguments={}):
        self.instance_extractor_func = getattr(instance_extractors,instance_extractor_name)
        self.arguments_instance_extractor = arguments
        
    def get_files(self):
        for folder in self.folder_list:
            for filename in glob.glob(os.path.join(folder,'*.%s' % self.folder_extension)):
                yield filename
        
    def get_instances(self,knaf_obj):
        for term_id, is_mfs in self.instance_extractor_func(knaf_obj,self.arguments_instance_extractor):
            yield term_id, is_mfs

    

if __name__ == '__main__':

    import argparse
    #argparse
    parser = argparse.ArgumentParser(description='Feature extractor')
    parser.add_argument('-c',           dest='competition', help='semcor | sval2013 | sval2015',                required=True)
    parser.add_argument('--rem_mon',    dest='rem_mon',     help="if given, monosemous instances are not used", action='store_true')
    args = parser.parse_args()    

    ##################################################################
    #Creating semcor16
    ##################################################################

    semcor16 = CorpusData('semcor16')
    semcor16.set_folder_list([__here__+'/resources/wsd_corpora/semcor1.6/brown1',
                              __here__+'/resources/wsd_corpora/semcor1.6/brown2',
                              __here__+'/resources/wsd_corpora/semcor1.6/brownv'])
    semcor16.set_folder_extension('naf')
    semcor16.set_instance_extractor('instance_extractor_semcor16')
    
    ##################################################################
   
    ##################################################################
    #Creating semeval2013 task12
    ################################################################## 
    
    
    semeval2013 = CorpusData('semeval2013#12')
    semeval2013.set_folder_list([__here__+'/resources/wsd_corpora/semeval2013_task12/en'])
    semeval2013.set_folder_extension('naf')
    these_arguments = {'path_to_wn_index':__here__+'/resources/wordnets/WordNet-3.0/dict/index.sense'}
    semeval2013.set_instance_extractor('instance_extractor_semeval2013',these_arguments)
    
    ##################################################################
    #Creating semeval2015 task13
    ################################################################## 
    
    
    path_identifiers    = os.sep.join([__here__,'resources','identifiers','sval2015.bin'])
    official_identifiers = cPickle.load(open(path_identifiers))

    semeval2015 = CorpusData('semeval2015#13')
    semeval2015.set_folder_list([__here__+'/resources/wsd_corpora/semeval2015_task13_en'])
    semeval2015.set_folder_extension('naf')
    these_arguments = {'path_to_wn_index':__here__+'/resources/wordnets/WordNet-3.0/dict/index.sense',
                       'official_identifiers': official_identifiers}
    semeval2015.set_instance_extractor('instance_extractor_semeval2015',these_arguments)

##################################################################
       
 
    ##################################################################
    # The feature extractors (the same for all corpora)
    ##################################################################
    sense_entropy_dict     = os.path.join(__here__,'resources','feature_input','sense-entropy_semcor.bin')
    idf_dict               = os.path.join(__here__,'resources','feature_input','idf.bin')
    cache_senses_wn30 = {}
    cache_senses_wn20 = {}
    WND_for_synset = {}
    
    feature_extractor_list = [('MFS_confidence_IMS','get_confidence_mfs_ofims',{'path_to_index_sense':__here__+'/resources/wordnets/WordNet-1.7.1/dict/index.sense', 'my_cache': {}}),
                              ('Entropy_sense_ranking_IMS', 'get_entropy_sense_ranking_ims171', {}),
                              ('num_senses', 'get_number_of_senses',{}),
                              ('idf',        'get_idf',{'dict': cPickle.load(open(idf_dict))}),  
                              ('jex',        'get_jex',{}),
                              ('pos', 'get_pos',{'to_int':True}),
                              ('sense_entropy','get_sense_entropy',{'dict': cPickle.load(open(sense_entropy_dict))}),
                              ('correlation_confidences_semcor_and_IMS','correlation_confidences_semcor_and_system',{'dict': cPickle.load(open(sense_entropy_dict)),
                                                                                                                     'resource': 'wn30g.bin64'}),
                              ('correlation_confidences_semcor_and_UKB','correlation_confidences_semcor_and_system',{'dict': cPickle.load(open(sense_entropy_dict)),
                                                                                                                     'resource': 'WordNet-3.0#IMS_original_models'}),
                              ('MFS_confidence_UKB','get_confidence_mfs_of_ukb30',{'path_to_index_sense':__here__+'/resources/wordnets/WordNet-3.0/dict/index.sense', 'my_cache_wn30':cache_senses_wn30}),
                              ('Entropy_sense_ranking_UKB','get_entropy_sense_ranking_ukb30',{}),
                              ('SuperSense_for_MFS','get_supersense_for_mfs',{'path_to_index_sense':__here__+'/resources/wordnets/WordNet-3.0/dict/index.sense', 'cache_senses_wn30':cache_senses_wn30}),
                              ('WND_for_MFS','get_WND_for_mfs',{'path_to_index_sense_wn20':__here__+'/resources/wordnets/WordNet-2.0/dict/index.sense',
                                                                'cache_senses_wn20':cache_senses_wn20, 'WND_for_synset': WND_for_synset,
                                                                'WND_file':__here__+'/resources/wn-domains-3.2/wn-domains-3.2-20070223',
                                                                'domains': []}),
                              ('ratio_WND','ratio_WND',{'path_to_index_sense_wn20':__here__+'/resources/wordnets/WordNet-2.0/dict/index.sense',
                                                        'cache_senses_wn20':cache_senses_wn20, 'WND_for_synset': WND_for_synset,
                                                        'WND_file':__here__+'/resources/wn-domains-3.2/wn-domains-3.2-20070223'})
                              ]
    
    ##################################################################
    
    ##################################################################
    # The corpora list with objects of the class CorpusData
    ##################################################################
    corpora_list        = []

    if args.competition == "sval2013":
        corpora_list.append(semeval2013)
        output_jex = os.sep.join([__here__,'resources','feature_input','train_semcor_test_sval2013.bin'])
    elif args.competition == "semcor":
        corpora_list.append(semcor16)
        output_jex = os.sep.join([__here__,'resources','feature_input','train_semcor_test_semcor.bin'])
    elif args.competition == "sval2015":
        corpora_list.append(semeval2015)
        output_jex          = os.sep.join([__here__,'resources','feature_input','train_semcor_test_sval2015.bin'])

    jex_dict = cPickle.load(open(output_jex))

    ##################################################################

    print>>sys.stderr, '#'*50
    print>>sys.stderr, 'START: %s' % time.strftime('%Y-%m-%dT%H:%M:%S%Z')
    print>>sys.stderr, '#'*50
     
    features_for_id = {}    # (termid,ismfs) --> 'type_feat' --> list_feats 
    N = 0
    num_corpus = num_files = num_pos = num_neg = 0
    for corpus in corpora_list:
        print>>sys.stderr,'Processing', corpus.get_id()
        num_corpus += 1
        for filename in corpus.get_files():
            num_files += 1
            print>>sys.stderr,'\t',filename
            my_obj = KafNafParser(filename)
            for term_id, is_mfs in corpus.get_instances(my_obj):
                
                #include check for polysemy here
                feature_extractor_function = getattr(feature_extractors,'get_number_of_senses_wordnet') 
                num_senses = feature_extractor_function(my_obj,term_id,{'num_senses':{}})
                
                #remove monosemous from training and testing
                if all([num_senses == '1',
                        args.rem_mon]):
                    continue

                if is_mfs: 
                    num_pos+=1
                else: 
                    num_neg += 1
                whole_id = filename+'---'+term_id
                features_for_id[(whole_id,is_mfs)] = {}
                for name_feat, feature_extractor_name, params in feature_extractor_list:
                    features_for_id[(whole_id,is_mfs)][name_feat] = []
                    feature_extractor_function = getattr(feature_extractors,feature_extractor_name)
                    for feature in feature_extractor_function(my_obj,term_id,params):

                        #do check here if the feature value is already in locals()
                        if name_feat == "num_senses":
                            feature = num_senses
                        if name_feat == "jex":
                            feature = str(jex_dict[whole_id])
                        
                        features_for_id[(whole_id,is_mfs)][name_feat].append(feature)
            N+=1
            #if N == 20:
            #    break       #Just for one file
    
    
    '''
    #FRIENDLY PRINTING 1
    for (tid, is_mfs), dict_features in features_for_id.items():
        print tid, is_mfs
        for name_feat, list_features in dict_features.items():
            print '  *** %s' % name_feat
            print '     ==> ',
            for feat in list_features:
                print feat,
            print
    '''
    
    feature_labels = [name_feat for name_feat, feature_extractor_name, params in feature_extractor_list]
    print '%s\t%s\t%s' % ('is_MFS', 'ID', '\t'.join(feature_labels))
    for (tid, is_mfs), dict_features in features_for_id.items():
        # dict_features[feat] is a list of features, we take the first one (if there are more than one value
        # there are problems to represent with this CSV/Matrix format
        values = [str(is_mfs),tid] + [dict_features[feat][0] for feat in feature_labels]    
        print '%s' % ('\t'.join(values))
        
    print>>sys.stderr, '#'*50
    print>>sys.stderr, 'END: %s' % time.strftime('%Y-%m-%dT%H:%M:%S%Z')
    print>>sys.stderr, '#'*50
    print>>sys.stderr, 'Num corpus: %d' % num_corpus
    print>>sys.stderr, 'Num files: %d' % num_files
    print>>sys.stderr, 'Num total instances: %d' % (num_pos+num_neg)
    print>>sys.stderr, '\tPositive: %d' % num_pos
    print>>sys.stderr, '\tNegative: %d' % num_neg
    print>>sys.stderr, 'Features: %s' % (' '.join(feature_labels))
    print>>sys.stderr, '#'*50
    
    sys.exit(0)
    
    
    
   
   
#    index_of_features = {}
#    features_for_id_class = {}
#    T = 0 
#    for corpus, corpus_description in corpus_data.items():
#        for folder in corpus_description['folder_list']:
#            print folder
#            for input_file in glob.glob(folder+'/*.'+corpus_description['folder_extension']):
#                naf_obj = KafNafParser(input_file)
#                print>>sys.stderr, 'Processing', input_file
#                #T+=1
#                #if T == 15:
#                #    break
#                instance_extractor_function = getattr(instance_extractors, corpus_description['instance_extractor'])
#                
#                for term_id, is_mfs in instance_extractor_function(naf_obj):
#                    whole_term_id = input_file+'#'+term_id
#                    features_for_id_class[(whole_term_id,is_mfs)] = []
#                    ##print '\t',term_id, is_mfs
#                    for feature_extractor_function_name, arguments in corpus_description['feature_extractor_list']:
#                        feature_extractor_function = getattr(feature_extractor,feature_extractor_function_name)
#                        for token in feature_extractor_function(naf_obj,term_id, arguments):
#                            ##print '\t\t',token
#                            features_for_id_class[(whole_term_id,is_mfs)].append(token)
#                            if token not in index_of_features:
#                                index_of_features[token] = len(index_of_features) + 1
#            #next folder
#            #break
#    
#                                
#    #Encode all the features
#    print 'Is_MFS File#termid',
#    for numfeat in xrange(1,len(index_of_features)+1):
#        print 'F%d' % (numfeat),
#    print    
#    T = 0
#    for (feature_id, is_mfs), list_tokens in features_for_id_class.items():
#        if T%100 == 0:
#            print>>sys.stderr,'%d instances processed out of %d' % (T, len(features_for_id_class))
#        T += 1
#        ##print feature_id
#        freq_for_feature_number = defaultdict(int)  #This will store the feature numbers -> frequency
#        for token in list_tokens:
#            freq_for_feature_number[index_of_features[token]] += 1
#            #print '\t',token,index_of_features[token]
#        print is_mfs, feature_id,
#        #For every feature possible we print the frequency in this case or 0 (not dense matrix)
#        for num_feat in xrange(1,len(index_of_features)+1):
#            print freq_for_feature_number[num_feat],
#        print 
#        
#    fd = open('dictionary','w')
#    for feat,index in index_of_features.items():
#        fd.write('%s  %d\n' % (feat,index))
#    fd.close()    
#    print>>sys.stderr, 'Dictionary in file dictionary'
#        
#    print>>sys.stderr, 'Number of instances',len(features_for_id_class)
#    print>>sys.stderr, 'Number of uniq',len(index_of_features)
    
