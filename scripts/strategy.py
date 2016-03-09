import os
import sys
from collections import defaultdict
from nltk.corpus import wordnet as wn
import nltk
import pickle
import plotting

#import random forest module
repo_folder = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'resources/repositories'))
sys.path.append(repo_folder)
from WordNetMapper import WordNetMapper

class Strategy():
    '''
    '''
    
    def __init__(self,data,args):
        
        self.output     = {}
        self.args = args
        self.sense_distribution = defaultdict(list)
        self.inspection = defaultdict(list)
        self.my_mapper  = WordNetMapper()
        self.n_performance = 0.0

        for identifier,info in data.iteritems():
            output = self.perform_strategy(info,args.strategy)
            self.output[identifier] = output
        
        #save to file
        output_path = os.path.join(args.output_folder,args.strategy)
        with open(output_path,'w') as outfile:
            pickle.dump(self.output,outfile)

        if args.strategy == "n": 
            
            output_path = os.sep.join([args.output_folder,"performance_n_per_pos.txt"])
            with open(output_path,"w") as outfile:
                for pos,value in self.inspection.iteritems():
                    outfile.write("\n")
                    outfile.write(pos+"\n")
                    outfile.write("number correct: %s\n" % value.count(True))
                    outfile.write("num_instances: %s\n"  % len(value))
                    outfile.write("perc correct: %s\n"   % (value.count(True) / float(len(value))))

        if self.inspection['all']: 
            self.n_performance = (self.inspection['all'].count(True) / float(len(self.inspection['all'])))
            self.n_performance = round(self.n_performance,3)

    def perform_strategy(self,info,strategy):

        '''
        perform strategy
        
        @type  info: dict
        @param info: containing info over instance semeval competition

        @type  strategy: str
        @param strategy: system | 
        
        @rtype: dict
        @return: dict containing information about strategy correctness
        '''

        #info about senses
        self.info            = info
        self.first_strategy  = ""
        self.correct         = False

        #get system and system sense number
        self.system()
        if info['monosemous']:
            self.first_sense     = info['mfs']
            self.first_strategy  = 'monosemous'
        
        #elif strategy == "system":
        #    self.system()
        
        elif strategy == "n":
            self.n()

        elif strategy == "p":
            self.p()
        
        elif strategy == "np":
            self.np()
       
        elif strategy == 'gold_classifier':
            self.gold_classifier()
 
        lexkey       = self.first_sense
        lexkey_mfs   = info['mfs']
        self.correct = lexkey in info['gold']
       
        strategy_sense_number = 0
        gold_key = info['gold'][0]
        if gold_key in self.args.lexkey2sense_number:
           sense_number = self.args.lexkey2sense_number[gold_key]
 
        #update sense distribution info
        self.sense_distribution[ self.info['polysemy'] ].append(lexkey == lexkey_mfs)
        self.sense_distribution[ 'all' ].append(lexkey == lexkey_mfs)

        return {     'correct'        : self.correct,
                     'lexkey'         : lexkey,
                     'ilidef'         : self.first_sense,
                     'strategy'       : self.first_strategy,
                     'identifier'     : info['identifier'],
                     'identifier2'    : info['identifier2'],
                     'mfs_classifier' : info['mfs_classifier'],
                     'doc'            : info['identifier'].split('.')[0],
                     'lemma'          : info['lemma'],
                     'pos'            : info['pos'],
                     'mfs'            : lexkey_mfs,
                     'gold'           : info['gold'],
                     'prev_lemma'     : info['prev_lemma'],
                     'prev_iden'      : info['prev_iden'],
                     'sense_number' : sense_number,
                     'polysemy' : self.info['polysemy']

                    }
    
    def mfs(self):
        '''
        return mfs based on ivar info
        '''
        self.first_strategy  = "mfs"
        self.first_sense     = self.info['mfs']
    
    def system(self):
        '''
        return system based on ivar info
        '''
        self.first_strategy = 'system'
        self.first_sense    = self.info['system']
           
        if self.first_sense:
            self.first_sense = self.my_mapper.map_ilidef_to_lexkey(self.first_sense,self.info['lemma'])            
        else:
            self.mfs()

    def p(self):
        '''
        this strategy works as follows:
            (a) if mfs_classifier == 1: go for mfs
            (b) else system
        '''
        if self.info['mfs_classifier'] == '1':
            self.mfs()

    def pick_second_confidence_sense(self):
        '''
        select sense with second highest confidence
        '''
        if len(self.info['system_all']) >= 2:
            confidence,self.first_sense = self.info['system_all'][1]
            self.first_sense  = self.my_mapper.map_ilidef_to_lexkey(self.first_sense,self.info['lemma'])

    def pick_second_sense(self):
        '''
        pick lemma.pos.2 as answer
        '''
        lemma = self.info['lemma']
        pos = self.info['pos']
        
        try:
            synset = wn.synset('{lemma}.{pos}.2'.format(**locals()))
        except nltk.corpus.reader.wordnet.WordNetError:
            return                    

        version = '30'
        offset        = str(synset.offset)
        length_offset = len(offset)
        zeros         = (8-length_offset)*'0'

        ilidef = "ili-{version}-{zeros}{offset}-{pos}".format(**locals())
        self.first_sense = self.my_mapper.map_ilidef_to_lexkey(ilidef,self.info['lemma'])
        
    def gold_classifier(self):
        '''
        use gold info to test performance of strategy n when mfs classifier would be perfect
        '''
        if all([self.info['mfs'] not in self.info['gold'],
                self.first_sense == self.info['mfs'] ]):
            self.pick_second_sense()

    def n(self):
        '''
        this strategy works as follows:
            (a) run system
            (b) if self.first_sense == self.info['mfs'] and self.info['mfs_classifier'] == '0', then change to second sense
        '''
        if all([self.info['mfs_classifier'] == '0',
                self.first_sense == self.info['mfs']]):
            self.pick_second_confidence_sense()
            self.first_strategy = "n"
        
            #for debugging
            debug = False
            if debug:
                print 
                print self.first_sense
                print self.info['system_all']
                gold_ili = [self.my_mapper.map_lexkey_to_ilidef(gold_key,'30','30') for gold_key in self.info['gold']]
                print gold_ili
                raw_input('continue?') 
            
            #for error analysis
            #lexkey       = self.my_mapper.map_ilidef_to_lexkey(self.first_sense,self.info['lemma']) 
            self.inspection[self.info['pos']].append( self.first_sense in self.info['gold'] ) 
            self.inspection['all'].append( self.first_sense in self.info['gold'] ) 
            
    def np(self):
        '''
        this strategy first runs self.p(), then self.n()
        '''
        self.p()
        self.n()
   

