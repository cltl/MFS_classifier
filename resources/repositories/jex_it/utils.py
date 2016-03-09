import subprocess
import os 
from scipy.stats.stats import pearsonr
from collections import defaultdict

#import external modules
from lxml import etree 
from KafNafParserPy import KafNafParser

def goodness_of_fit(d1,d2):
    '''
    given two dicts mapping from domain to weight of domain
    this method returns the similarity based on the pearson correlation
    
    @type  d1: dict
    @param d1: mapping from domain -> weight (float)

    @type  d2: dict
    @param d2: mapping from domain -> weight (float)
    
    @rtype: float
    @return: pearson r correlation
    '''
    all_domains = set( d1.keys() + d2.keys())
    
    #check if one of the dicts is empty, return 0.0
    if {} in [d1,d2]:
        return 0.0 

    v1      = []
    v2      = []
    default = 0.0 

    for domain in all_domains:
        
        if domain in d1:    
            v1.append(d1[domain])
        else:
            v1.append(default)

        if domain in d2:
            v2.append(d2[domain])
        else:
            v2.append(default)

    correlation,p_value = pearsonr(v1,v2)

    return correlation        
        
    
def call_jex(path_to_jex_dir):
    '''
    given the path to JEX dir, this module calls it from python
    
    @requires: subprocess
    
    @type  path_to_jex_dir: str
    @param path_to_jex_dir: full path to JEX domain classifier
    
    @rtype: str
    @return: std.out is returned if exit code was 0, else CalledProcessError
    is raised.
    '''
    #create command to call jex (go to /bin folder and call AllinOneStep.sh
    command = "&&".join(["cd %s/bin" % path_to_jex_dir,
                         "bash AllInOneStep.sh"])
    
    #call it
    std_out = subprocess.check_output(command,shell=True)
    
    return std_out

def create_input_jex(d_id_to_sent_ids,d_sent_ids_to_sents,path_to_jex_dir):
    '''
    given a mapping from id to a list of sentences in which this id occurs
    and a mapping from sent_ids to the sentence in questions, this method
    will create the input files for the jex domain classifier
    
    @type  d_id_to_sent_ids: collections.defaultdict
    @param d_id_to_sent_ids: mapping from an id to a list of sent_ids in
    which this id occurs
    
    @type  d_sent_ids_to_sents: collections.defaultdict
    @param d_sent_ids_to_sents: mapping from a sent_id to the sentence itself
    
    @type  path_to_jex_dir: str
    @param path_to_jex_dir: full path to JEX domain classifier
    '''
    documents_dir_jex = os.path.join(path_to_jex_dir,"documents")
    
    #empty documents folder
    subprocess.call("rm -r %s/documents/ && mkdir %s/documents" % (path_to_jex_dir,path_to_jex_dir),shell=True)
    subprocess.call("rm -r %s/result/PostProcessedDocs/ && mkdir %s/result/PostProcessedDocs/" % (path_to_jex_dir,path_to_jex_dir),shell=True)

    for identifier,list_sent_ids in d_id_to_sent_ids.iteritems():
        
        identifier = identifier.encode("utf-8")  
        identifier = identifier.replace("&","")

        output_path = os.path.join(documents_dir_jex,
                                   "{identifier}.txt".format(**locals()))
        
        
        try:
            with open(output_path,"w") as outfile:
                for sent_id in list_sent_ids:
                    sentence = " ".join(d_sent_ids_to_sents[sent_id])
                    sentence = sentence.encode("utf-8")
                    outfile.write(sentence + "\n")
        except IOError:
            continue


def read_output_jex(path_to_output_jex):
    '''
    given an output xml from jex domain classifier, this module
    extracts the domain information
    
    @type  path_to_output_jex: str
    @param path_to_output_jex: full path to output xml jex
    
    @rtype: dict
    @return: mapping from domain to weight of domain (float)
    '''
    doc = etree.parse(path_to_output_jex)
    
    output = {category_el.get("label"): float( category_el.get("weight") )
              for category_el in doc.iterfind("category")}
    
    return output

def jex_results_to_dict(path_to_jex,d_id_to_sent_ids):
    '''
    all results from jex are loaded into one dict

    @type  path_to_jex: str
    @param path_to_jex: full path to jex domain classifier

    @type  d_id_to_sent_ids: collections.defaultdict
    @param d_id_to_sent_ids: mapping from an id to a list of sent_ids in
    
    @rtype: dict
    @return: mapping from identifier -> domain -> weight (float). weight is 0.0
    if output jex is not found (can be for various reasons)
    '''
    results            = defaultdict(dict)
    results_folder_jex = os.sep.join([path_to_jex,"result","PostProcessedDocs"])

    for identifier in d_id_to_sent_ids:
        
        path_to_output_jex = os.sep.join([results_folder_jex,identifier+".txt"])
        if os.path.exists(path_to_output_jex):
            output = read_output_jex(path_to_output_jex) 
        else:
            output = {}
        
        results[identifier] = output
    return results

def path_generator(base_dir,extention):
    '''
    given a base directory containing possible subdirectories
    this method returns a generator with all paths with a certain extention.
    
    @type  base_dir: str
    @param base_dir: full path to directory
    
    @type  extention: str
    @param extention: wanted extention, for example '.bz2'
    
    @rtype:  generator
    @return: generator all paths with param extention
    ''' 
    for (dirpath, dirnames, filenames) in os.walk(base_dir):
        for filename in filenames:
            if filename.endswith(extention): 
                yield os.sep.join([dirpath, filename])

def get_sent_id(wid_to_sent_id,term_el):
    '''
    obtain sent_id from term_el

    @type  wid_to_sent_id: dict
    @param wid_to_sent_id: mapping from wid to sent_id

    @type  term_el: lxml.etree._Element
    @param term_el: lxml term element from naf

    @rtype: str
    @return: sent_id of term_el
    '''        
    span_ids  = term_el.get_span().get_span_ids()
    target_id = span_ids[0][1:]
    
    sent_id   = wid_to_sent_id[target_id]

    return sent_id

def run_jex(input_folder,args,lemma=False,document=False):
    '''
    given an input naf, this function runs the jex domain classifier.

    @type  input_folder: str
    @param input_folder: full path to folder containing naf files

    @type  args: namespace
    @param args: namespace containing command line arguments values

    @type  lemma: bool
    @param lemma: if True, jex is run on all occurences of each lemma

    @type  document: bool
    @param document: if True, jex is run on every document separately
    
    @rtype: collections.defaultdict
    @return: mapping from lemma or basename to output jex (which is mapping from domain to confidence)
    '''   
    #loop over naf files
    #(1) create d_id_to_sent_ids
    #(2) create d_sent_ids_to_sents
    d_id_to_sent_ids   = defaultdict(set)
    d_sent_ids_to_sent = defaultdict(list)

    for naf_file in path_generator(input_folder,".naf"):
        
        print len(d_id_to_sent_ids)
        #parse naf_file and obtain basename (used for sent_id later)
        try:
            doc      = KafNafParser(naf_file)
            basename = os.path.basename(naf_file)
        except IOError:
            continue
        
        #obtain dict from id to sentence number
        wid_to_sent_id = {wf_el.get_id()[1:]: wf_el.get_sent()
                          for wf_el in doc.get_tokens()}
        
    
        #update d_id_to_sent_ids
        if lemma:
            [d_id_to_sent_ids[term_el.get_lemma()].update( [(basename,get_sent_id(wid_to_sent_id,term_el))] )
             for term_el in doc.get_terms()]
 
        #update d_sent_ids_to_sents
        [d_sent_ids_to_sent[(basename,wf_el.get_sent())].append(wf_el.get_text())
        for wf_el in doc.get_tokens()]
    
        if document:
            #add documents to d_id_to_sent_ids
            [d_id_to_sent_ids[basename].update( [(basename,wf_el.get_sent())] )
             for wf_el in doc.get_tokens()]
    
    #create input jex and call jex
    create_input_jex(d_id_to_sent_ids,
                     d_sent_ids_to_sent,
                     args.jex_folder)
    
    call_jex(args.jex_folder)

    results = jex_results_to_dict(args.jex_folder,d_id_to_sent_ids)

    return results

