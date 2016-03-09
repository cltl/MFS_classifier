from training import train 
from testing import test
from evaluate import evaluate

def random_forest(path_train,
                  path_test,
                  name_identifiers,
                  name_targets,
                  features,
                  delimiter,
                  num_cores=1):
    '''
    this method performs the training,testing and evaluation of the
    random forest algorithm.
    
    @type  path_train: str
    @param path_train: full path to csv (first line contains headers).
    delimiter should be specified with param delimiter
    
    @type  path_test: str
    @param path_test: full path to csv (first line contains headers).
    delimiter should be specified with param delimiter

    @type  name_identifiers: str
    @param name_identifiers: name of column containing identifiers
    
    @type  name_targets: str
    @param name_targets: name of column containing targets
    
    @type  features: str 
    @param features: list of features to be used
    
    @type  delimiter: str
    @param delimiter: delimiter used in csv. tested with "," and "\t"
    
    @type  num_cores: int
    @param num_cores: [optional]: num of cores you want to use in training
    
    @rtype: tuple
    @return: (output_classifier,evaluation). both are dicts. output_classifier
    maps identifier -> output_classifier. evaluation maps all kinds of evaluation metrics
    to floats.
    '''
    #call train using class
    identifiers_training,target_training,rf = train(path_train,
                                                  name_identifiers,
                                                  name_targets,
                                                  features,
                                                  output_path_model=None,
                                                  cores=num_cores,
                                                  the_delimiter=delimiter)
    
    #call test using class
    identifiers_test,target,prediction    = test(path_test,
                                                 name_identifiers,
                                                 name_targets,
                                                 features,
                                                 loaded_rf_model=rf,
                                                 path_rf_model=None,
                                                 the_delimiter=delimiter)
    
    #evaluate
    classifier_output,evaluation = evaluate(target, prediction, identifiers_test)
    
    return classifier_output,evaluation