from tabulate import tabulate
import argparse
import os 
from collections import defaultdict

parser = argparse.ArgumentParser(description='Convert output wsd to latex tables')

parser.add_argument('-i', dest='input_folder', help='folder or file with output wsd', required=True)
parser.add_argument('-c', dest='competition', help='sval2013 | sval2015', required=True)
parser.add_argument('-o', dest='output_path', help='full output path', required=True)
args = parser.parse_args()
args.input_folder=os.path.join(args.input_folder,args.competition)


def extract(path,
            system1,
            system2,
            features):
    '''
    given a tsv file , this method extract the info of two systems.
    
    @type  path: str
    @param path: full path to tsv (first line keys, rest of lines first column system name
    and rest of columns float or integers values)
    
    @type  system1: str
    @param system2: name of system 1
    
    @type  system2: str
    @param system2: name of system 2
    
    @type  features: list
    @param features: list of features (need to be in first line of file)
    
    @rtype: defaultdict
    @return: defaultdict mapping a strategy to a mapping of measure -> score 
    '''
    #load into dict
    data = defaultdict(dict)
    
    with open(path) as infile:
        for counter,line in enumerate(infile):
            split = line.strip().split("\t")
            if counter == 0:
                keys = split
                indices = {feature:keys.index(feature)
                           for feature in features}
            else:
                values   = split
                strategy = split[0]
            
                if strategy in [system1,system2]:
                    for feature in features:
                        value = float(values[indices[feature]]) * 100
                        data[strategy][feature] = round(value,3)

    return data



#create table
def create_table(headers,features,output_path):
    headers=['\\textbf{%s}' % header for header in headers]
    ukb=extract(args.input_folder+".csv-UKB/results.csv","system","n",features)
    ims=extract(args.input_folder+".csv-IMS/results.csv","system","n",features)

    table=[]
    for system,d in [("UKB",ukb),("IMS",ims)]:
        line =  [system]+[d['system'][feature] for feature in features]
        line2 =  [system+"+classifier"]+[d['n'][feature] for feature in features]
        table.extend([line,line2])


    #adapt table with label + caption
    latex = "\\begin{table}[!h]"
    latex += tabulate(table,headers,tablefmt="latex_booktabs")
    for old,new in [("textbackslash{}",""),
                    ("\\{","{"),
                    ("\\}","}"),
                    ("lrrr","l c c c c")
                    
                    ]:
        latex = latex.replace(old,new)
    latex= latex.replace("\\hline\n","\\label{tab:wsd%s}\n" % args.competition,1)
    latex= latex.replace("\\hline\n","\\hline\\hline\n",1)
    latex = latex.replace("\n\\hline\n","\n")
    latex += "\n\\caption{TODO}\n"
    latex += "\\end{table}\n"
    #save table to file
    with open(output_path,"w") as outfile:
        outfile.write(latex)

#create wsd table
create_table(['Pwsd','Rwsd','Rwsd lfs'],['Pwsd','Rwsd','Rwsd_lfs'],args.output_path)
create_table(['Pbin','Rbin','ACCbin','TN rate'],['Pbin','Rbin','ACCbin','TN_rate'],args.output_path+'.mfs')
