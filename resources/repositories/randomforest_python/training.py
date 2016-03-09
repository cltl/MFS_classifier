#import installed modules
from sklearn.ensemble import RandomForestClassifier
import cPickle
import utils 

def train(path_to_training,
          name_identifiers,
          name_targets,
          features,
          output_path_model=None,
          cores=None,
          num_trees=100,
          the_delimiter=","):
    '''
    train Random Forest classifier
    
    @requires: sklearn (version 0.15.2 was used)
    @requires: numpy   (version 1.8.0rc1 was used)
    @requires: cPickle (version 1.71 was used)
    
    @type  path_to_training: str
    @param path_to_training: full path to comma separated file (first line contains headers)
    
    @type  name_identifiers: str
    @param name_identifiers: name of column containing identifiers
    
    @type  name_targets: str
    @param name_targets: name of column containing targets
    
    @type  features: str 
    @param features: list of features to be used

    @type  output_path_model: None | str
    @param output_path_model: optional argument, default is None. If provided
    the model will be written to file using cPickle.
    
    @type  cores: int
    @param cores: optional arguments. Default is None. If provided, that number
    of cores will be used to run the training. 
    
    @type  num_trees: int
    @param num_trees: [optional]. default is 100.
    
    @type  the_delimiter: str
    @param the_delimiter: , \t is tested
    
    @rtype: tuple
    @return: tuple (identifiers,sklearn.ensemble.forest.RandomForestClassifier)
    '''
    identifiers,target,train   = utils.data_identifiers(path_to_training,
                                                        the_delimiter,
                                                        name_identifiers,
                                                        name_targets,
                                                        features)
    
    #create and train the random forest
    #multi-core CPUs can use: rf = RandomForestClassifier(n_estimators=100, n_jobs=2)
    if cores:
        rf = RandomForestClassifier(n_estimators=num_trees, n_jobs=cores)
    else:
        rf = RandomForestClassifier(n_estimators=num_trees)
    
    #train model
    rf.fit(train, target)
    
    #save model if wanted
    if output_path_model:
        cPickle.dump((identifiers,rf),open(output_path_model,"w"))
    
    #return model
    return (identifiers,target,rf)

