


def evaluate(gold, system, identifiers_test):
    '''
    given two lists of equal length containing zeros and ones
    in addition a mapping is created mapping the identifiers to the output of
    the classifier
    '''
    TP=0.0
    FP=0.0
    TN=0.0
    FN=0.0
    
    for index in xrange(len(gold)):
        
        g = int(gold[index])
        s = int(system[index])
        
        values = [g,s]
        
        if values == [0,0]:
            TN +=1
        elif values == [1,1]:
            TP +=1
        elif values == [1,0]:
            FN +=1
        elif values == [0,1]:
            FP +=1
        
        try:
            TN_rate =  TN / (FP+TP)
        except ZeroDivisionError:
            TN_rate = 0.0

        try:
            TP_rate =  TP / (TP+FN)
        except ZeroDivisionError:
            TP_rate = 0.0
        
        #accuracy
        accuracy = (TP + TN) / (TP + TN + FP + FN)
        
        classifier_output = {iden: is_mfs
                             for iden,is_mfs in zip(identifiers_test,system)}
                             
    return classifier_output,  {'TP_rate'       : TP_rate,
                                'TN_rate'       : TN_rate,
                                'accuracy'      : accuracy,
                                'FP'            : FP,
                                'FN'            : FN,
                                'TP'            : TP,
                                'TN'            : TN,
                                'num_instances' : len(system),
                                'gold'          : gold}

