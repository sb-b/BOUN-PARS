# BOUN-Pars

BOUN-Pars is a deep learning-based dependency parser developed for Turkish. It is based on Stanford's graph-based neural dependency parser and uses linguistically oriented rules and benefits from morphological information of words.

BOUN-Pars creates dependency parse trees of Turkish sentences in CoNLL-U format.

The pre-processing steps of parsing from raw text: the segmentation, morphological tagging, and lemmatization tasks are performed by a pre-trained model by [TurkuNLP pipeline](https://turkunlp.org/Turku-neural-parser-pipeline/).

# Installation

The required packages for the pre-trained TurkuNLP pipeline model is listed [here](https://turkunlp.org/Turku-neural-parser-pipeline/install.html). 
 

BOUN-Pars is developed by Şaziye Betül Özateş, Arzucan Özgür, Tunga Güngör from in the Department of Computer Engineering, and Balkız Öztürk from in the Department of Linguistics , at Bogazici University. 

Please cite the following papers if you make use of this tool:

```
@article{ozates2020hybrid,
         author ={Şaziye Betül Özateş,  Arzucan Özgür, Tunga Güngör, Balkız Öztürk},
         title ={A Hybrid Approach to Dependency Parsing: Combining Rules and Morphology with Deep Learning},
         journal ={Computational Linguistics Journal (Under Review)}}
```
