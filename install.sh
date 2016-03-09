
#create dirs if they not exist
export cwd=/${PWD#*/}
export resources=$cwd/resources/
export repos=$resources/repositories
export feature_input=$resources/feature_input
export identifiers=$resources/identifiers
export scorers=$resources/scorers

mkdir -p $repos
mkdir -p $feature_input
mkdir -p $identifiers
mkdir -p $scorers

#sense entropy semcor
#scripts and output is located at: https://github.com/cltl/WSD_error_analysis (script is lib/sense_entropy.py)
function sense_entropy_wordnet () {

cd $repos
git clone https://github.com/cltl/WSD_error_analysis.git
cp WSD_error_analysis/lib/WordNet-eng30_synset $feature_input/sense-entropy_semcor.bin
rm -rf WSD_error_analysis
}

#wordnetmapper repo
function wordnetmapper () {

cd $repos
git clone --depth=1 https://github.com/MartenPostma/WordNetMapper.git
}

function get_scorers() {

cd $scorers
wget "http://www.cs.york.ac.uk/semeval-2013/task12/data/uploads/datasets/semeval-2013-task12-test-data.zip"
unzip semeval-2013-task12-test-data.zip

wget "http://alt.qcri.org/semeval2015/task13/data/uploads/semeval-2015-task-13-v1.0.zip"
unzip semeval-2015-task-13-v1.0.zip

}


function jex () {

cd $resources/repositories/jex_it
wget "http://optima.jrc.it/Resources/Eurovoc/indexing/en-eurovoc-1.0.zip"
unzip en-eurovoc-1.0.zip
}

#########################################
#call functions

gunzip resources/feature_input/train_semcor_test_semcor.bin.gz

sense_entropy_wordnet

wordnetmapper

get_scorers

jex
