import matplotlib.pyplot as plt
from collections import defaultdict 
import argparse

def plot_it(path,
            system1,
            system2,
            features,
            title,
            output_path):
    '''
    given a tsv file , this method plots the
    difference between two systems.
    
    @type  path: str
    @param path: full path to tsv (first line keys, rest of lines first column system name
    and rest of columns float or integers values)
    
    @type  system1: str
    @param system2: name of system 1
    
    @type  system2: str
    @param system2: name of system 2
    
    @type  features: list
    @param features: list of features (need to be in first line of file)
    
    @type  output_path: str
    @param output_path: output_path (.pdf)
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
                        data[strategy][feature] = float(values[indices[feature]]) * 100
    
    
        
    #plot it
    fig      = plt.figure()
    ax       = fig.add_subplot(111)
    x_axis   = [0,1]
    x_values = [system1,system2]
    
    for feature in features:
        y    = [data[strategy][feature] for strategy in [system1,system2]]
        diff = (y[1]-y[0])
        prefix = ""
        if diff > 0:
            prefix = "+"
        label = "%s (%s%s)" % (feature,prefix,diff)
        plt.plot(x_axis,y,label=label)
    
    #try to fit xlabel in plot
    #plt.gcf().subplots_adjust(bottom=0.20)
    
    plt.title(title)
    plt.xlabel("strategy")
    plt.ylabel("performance")
    plt.xticks(range(len(x_values)), x_values, size='small')
    #plt.xticks(rotation=90)
    ax.legend(loc='center')
    plt.savefig(output_path)


#parse arguments
parser = argparse.ArgumentParser(description='Plot results mfs classifier')
    
parser.add_argument('-i', dest='path',             help='full path to results.csv',  required=True)
parser.add_argument('-t', dest='title',            help='graph title',               required=True)
parser.add_argument('-o', dest='output_path',      help='output path (.pdf)',        required=True)
args = parser.parse_args()



plot_it(args.path,
        "system",
        "n",
        ["bin_acc","recall","accuracy_non_mfs"],
        args.title,
        args.output_path)
