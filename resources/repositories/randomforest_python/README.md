#Random Forest#

This repo provides python module to train, test and evaluate the random forest algorithm.
It was based on a code snippet from (https://www.kaggle.com/wiki/GettingStartedWithPythonForDataScience).

##USAGE##
git clone this repository.
```shell
python

>>>import RandomForest

#please check the attributes README, LICENSE AND INSTALL before using
>>> print(RandomForest.README)
>>> print(RandomForest.LICENSE)
>>> print(RandomForest.INSTALL)

#example of how to use it
>>> classifier_output,evaluation =RandomForest.random_forest(RandomForest.path_train,
											                RandomForest.path_test,
											                "ID",
											                "is_MFS",
											                ["num_senses","pos"],
											                "\t",
											                num_cores=1)
>>> evaluation['accuracy']											 
0.5510360706062931
```	                  
##Contact##
* Marten Postma
* m.c.postma@vu.nl
* http://martenpostma.com/
* Free University of Amsterdam
