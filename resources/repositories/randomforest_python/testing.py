import cPickle
import utils 

def test(test_csv,
         name_identifiers,
         name_targets,
         features,
         loaded_rf_model=None,
         path_rf_model=None,
         the_delimiter=","):
    '''
    test RandomForest classifier (one of the optional arguments has to provided)
    
    @type  test_csv: str
    @param test_csv: full path to test csv
    
    @type  name_identifiers: str
    @param name_identifiers: name of column containing identifiers
    
    @type  name_targets: str
    @param name_targets: name of column containing targets
    
    @type  features: str 
    @param features: list of features to be used

    @type  loaded_rf_model: None | str
    @param loaded_rf_model: optional argument. If provided, this argument will
    be used as trained model
    
    @type  path_rf_model: None | str
    @param path_rf_model: optional argument. If provided, model will be loaded
    using cPickle
    
    @type  the_delimiter: str
    @param the_delimiter: "," and "\t" is tested

    @rtype: 3-tuple
    @return: identifiers,target,prediction
    '''
    
    #load model if needed
    if path_rf_model:
        rf = cPickle.load(open(path_rf_model))
    else:
        rf = loaded_rf_model
    
    #load test csv
    identifiers,target,test = utils.data_identifiers(test_csv,
                                                     the_delimiter,
                                                     name_identifiers,
                                                     name_targets,
                                                     features)
    
    #test Random Forest classifier
    prediction = [x for x in  rf.predict(test)]
    
    return identifiers,target,prediction

