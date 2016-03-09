import os

#import function to train classifier
from training import train

#import function to test classifier
from testing import test

#import function to evaluate
from evaluate import evaluate

#import function to do full process
from random_forest import random_forest

#example training,test file
cwd             = os.path.dirname(os.path.realpath(__file__))
path_train      = os.path.join(cwd,"example","semcor_mfs.csv")
path_test       = os.path.join(cwd,"example","semeval2013_mfs.csv")

#documentation attributes
README         = open(os.path.join(cwd,"README.md")).read()
LICENSE        = open(os.path.join(cwd,"LICENSE.md")).read()
INSTALL        = open(os.path.join(cwd,"INSTALL.md")).read()
__author__     = "Marten Postma"
__license__    = "Apache"
__version__    = "1.0"
__maintainer__ = "Marten Postma"
__email__      = "martenp@gmail.com"
__status__     = "development"
