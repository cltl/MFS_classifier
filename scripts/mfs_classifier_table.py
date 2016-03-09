from tabulate import tabulate
import argparse
import os 
import cPickle

parser = argparse.ArgumentParser(description='Convert output mfs classifier to latex tables')

parser.add_argument('-i', dest='input_folder', help='folder or file with output wsd', required=True)
parser.add_argument('-o', dest='output_path', help='full output path', required=True)
args = parser.parse_args()



#create table
headers=['\\textbf{%s}' % header for header in ['competition-','accuracy','% of']]
headers2=['\\textbf{system}','\\textbf{(polysemy 2\\textgreater)}','\\textbf{instances}']

table = [headers2]
for competition in ['sval2013','sval2015']:
    for system in ["-UKB","-IMS"]:
        bin_path = os.path.join(args.input_folder,
                                '{competition}.csv{system}'.format(**locals()),
                                'best_setting.bin')
        info = cPickle.load(open(bin_path))
        line     = [competition+system,
                    round(info['best_polysemous_accuracy'] * 100,1),
                    round(info['perc_of_instances'] * 100,1)]
        table.append(line)

#adapt table with label + caption
latex = "\\begin{table}[!h]\n"
latex += tabulate(table,headers,tablefmt="latex_booktabs")
for old,new in [("textbackslash{}",""),
                ("\\{","{"),
                ("\\}","}"),
                ("lll","l c c"),
                ('sval2013-UKB','\\hline\\hline\nsval2013-UKB') 
                ]:
    latex = latex.replace(old,new)
latex= latex.replace("\\hline\n","\\label{tab:mfs_classifier}\n",1)
latex = latex.replace("\n\\hline\n","\n")
latex += "\n\\caption{TODO}\n"
latex += "\\end{table}\n"
#save table to file
with open(args.output_path,"w") as outfile:
    outfile.write(latex)
