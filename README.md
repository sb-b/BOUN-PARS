# BOUN-Pars

BOUN-Pars is a deep learning-based dependency parser developed for Turkish. It is based on [Stanford's graph-based neural dependency parser](https://github.com/tdozat/Parser-v2) and uses linguistically oriented rules and benefits from morphological information of words.

BOUN-Pars creates dependency parse trees of Turkish sentences in CoNLL-U format.

The pre-processing steps of parsing from raw text: the segmentation, morphological tagging, and lemmatization tasks are performed by a pre-trained model by [TurkuNLP pipeline](https://turkunlp.org/Turku-neural-parser-pipeline/).

# Installation

The required packages for the pre-trained TurkuNLP pipeline model is listed [here](https://turkunlp.org/Turku-neural-parser-pipeline/install.html). 

After successfully installed the pre-trained TurkuNLP pipeline model, do the following steps:

* Navigate to Turku-neural-parser-pipeline folder.
* Clone the parser:
```
git clone https://github.com/sb-b/BOUN-PARS.git
```
* Put everything inside BOUN-PARS folder into Turku-neural-parser-pipeline folder:
```
mv BOUN-PARS/* .
```
* Navigate to Parser-hybrid/saves folder.

* Download and unpack the pre-trained morphology-based parser model :
```
wget http://tabilab.cmpe.boun.edu.tr/BOUN-PARS/model_tr_imst_ruled_morphed.tgz
tar -xvf model_tr_imst_ruled_morphed.tgz
```

## Parse CoNLL-U File
To parse a CoNLL-U file, run the following command in Turku-neural-parser-pipeline folder:
```
sh parse-from-conllu.sh input.conllu output.conllu
```


## Parse Raw Text
In Turku-neural-parser-pipeline folder, run parse-text.sh:

```
sh parse-text.sh "bu örnek bir cümledir."
```


 

BOUN-Pars is developed by Şaziye Betül Özateş, Arzucan Özgür, Tunga Güngör from the Department of Computer Engineering, and Balkız Öztürk from the Department of Linguistics, at Bogazici University. 

Please cite the following papers if you make use of this tool:

```
@article{ozates2020hybrid,
         author ={Şaziye Betül Özateş,  Arzucan Özgür, Tunga Güngör, Balkız Öztürk},
         title ={A Hybrid Approach to Dependency Parsing: Combining Rules and Morphology with Deep Learning},
         journal ={Under Review}}
```
