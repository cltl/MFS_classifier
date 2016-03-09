import argparse
from glob import glob
from collections import defaultdict
import os

parser = argparse.ArgumentParser(description='Feature analysis overview')
    
parser.add_argument('-i', dest='in_folder',    help='path to input folder',     required=True)
parser.add_argument('-s', dest='suffix',       help='suffix ',      required=True)
args = parser.parse_args()


data = { "sval2013" : defaultdict(dict),
         "sval2015" : defaultdict(dict)}
features = set()

for ablation_csv in glob(args.in_folder+"/*.ablation.csv"):
    com,system,ablation = os.path.basename(ablation_csv).split(".csv.")

    with open(ablation_csv) as infile:
        for counter,line in enumerate(infile):
            if counter == 0:
                continue
            key,value = line.strip().split("\t")
            try:
                value = round( (float(value)*100), 2)
            except ValueError:
                pass
            
            data[com][system][key] = value

            if key.startswith("-"):
                features.update([key])

output_path = os.path.join(args.in_folder,"feature_analysis.csv")
first_two   = ["worst_value","best_value"]
print features
with open(output_path,"w") as outfile:
    outfile.write("\tsval2013\t\tsval2015\t\t\n")
    outfile.write("\tUKB\tIMS\tUKB\tIMS\n")
    for key in first_two:
        outfile.write("%s\t%s\t%s\t%s\t%s\n" % (key,
                                                data["sval2013"]["UKB"][key],
                                                data["sval2013"]["IMS"][key],
                                                data["sval2015"]["UKB"][key],
                                                data["sval2015"]["IMS"][key]))
    for feature in features:
        if feature in first_two:
            continue
        
        output = [feature]
        for com in ["sval2013","sval2015"]:
            for system in ["UKB","IMS"]:
                if feature in data[com][system]:
                    output.append( "-"+str(data[com][system][feature]))
                else:
                    output.append("NA")
        outfile.write("\t".join(output)+"\n")
                
                
