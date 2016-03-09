import argparse
import cPickle

#parse input arguments
parser = argparse.ArgumentParser(description="Create a mapping from identifier to gold keys + .nomw file will be created to evaluate")

parser.add_argument("-c", dest="competition", help="sval2013 | sval2015",              required=True)
parser.add_argument("-i", dest="input_path",  help="full path to file with gold keys", required=True)
parser.add_argument("-o", dest="output_path", help="path where output will be stored", required=True)

args = parser.parse_args()

def identifieris_sval2015(path):
    '''
    create mapping identifiers to gold sense keys sval2015
    
    @type  path: str
    @param path: path to gold keys of sval2015
    
    @rtype: dict
    @return: mapping from identifier to list of gold keys
    '''
    mapping = {}
    
    with open(path) as infile:
        with open(path+'.nomw','w') as outfile:
            for line in infile:
                split               = line.strip().split()
                identifier          = split[0]
                gold_keys           = [item[3:] for item in split if item.startswith('wn:')]
                mw                  = split[0] != split[1]
     
                if gold_keys:
                    if all(['_' not in gold_key for gold_key in gold_keys]):
                        mapping[identifier] = {'gold_keys' : gold_keys,
                                           'mw'        : mw}
                        
                        #if mw:
                        #    mapping[split[1]] = {'gold_keys'   : gold_keys,
                        #                          'mw'        : mw} 
                        outfile.write(line)
    return mapping

if args.competition == "sval2013":
    mapping = {}
    with open(args.input_path) as infile:
        with open(args.input_path+'.nomw','w') as outfile:
            for line in infile:
                gold_keys = line.strip().split()[2:]
                if any(['_' in gold_key for gold_key in gold_keys]):
                    continue
                identifier = line.strip().split()[1]
                mapping[identifier] = {'gold_keys': gold_keys, 'mw': False}
                outfile.write(line)

elif args.competition == "sval2015":
    mapping = identifieris_sval2015(args.input_path)

print
print(args.competition)
print(len(mapping))
print(args.input_path)
with open(args.output_path,"w") as outfile:
    cPickle.dump(mapping,outfile)
