import numpy as np

def data_identifiers(path_to_csv,
                     the_delimiter,
                     name_identifiers,
                     name_targets,
                     features):
    '''
    this method uses the numpy.genfromtxt to extract information from csv file
    
    @type  path_to_csv: str
    @param path_to_csv: full path to csv
    
    @type  the_delimiter: str
    @param the_delimiter: csv sep (comma and tab tested)
    
    @type  name_identifiers: str
    @param name_identifiers: name of column containing identifiers
    
    @type  name_targets: str
    @param name_targets: name of column containing targets
    
    @type  features: str 
    @param features: list of features to be used
    
    @rtype: tuple
    @return: (identifiers,targets,csv)
    '''
    #combine all headers
    features = features
    
    identifiers = []
    targets     = []
    #get index headers
    with open(path_to_csv) as infile:
        for counter,line in enumerate(infile):
            
            split         = line.strip().split(the_delimiter)
            
            if counter == 0:
                index_iden    = split.index(name_identifiers)
                targets_iden  = split.index(name_targets)
                index_headers = [index
                                 for index,value in enumerate(split)
                                 if value in features]
            else:
                identifiers.append(split[index_iden])
                targets.append(split[targets_iden]) 
        
    #read csv using pandas
    csv = np.genfromtxt(path_to_csv,
                        delimiter=the_delimiter,
                        usecols=index_headers)[1:]
    
    #convert to array
    csv = np.array(csv) 

    return (identifiers,targets,csv)

