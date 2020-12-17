# BOUN-Pars

BOUN-Pars is a deep learning-based dependency parser developed for Turkish. It is based on [Stanford's graph-based neural dependency parser](https://github.com/tdozat/Parser-v2) and uses linguistically oriented rules and benefits from morphological information of words.

BOUN-Pars creates dependency parse trees of Turkish sentences in CoNLL-U format.

The pre-processing steps of parsing from raw text: the segmentation, morphological tagging, and lemmatization tasks are performed by a pre-trained model by [TurkuNLP pipeline](https://turkunlp.org/Turku-neural-parser-pipeline/).

# Installation

* This program requires Turku-neural-parser-pipeline. Run the following commands
```
git clone --depth 1 https://github.com/tabilab-dip/Turku-neural-parser-pipeline-BPARS.git
cd Turku-neural-parser-pipeline-BPARS
git submodule update --init --recursive
python3.7 -m venv venv-parser-neural
source venv-parser-neural/bin/activate
pip3 install wheel
pip3 install -r requirements-cpu.txt
wget http://tabilab.cmpe.boun.edu.tr/BOUN-PARS/model_tr_imst_ruled_morphed_pipeline.tgz
tar -xvf model_tr_imst_ruled_morphed_pipeline.tgz
git clone --depth=1 --branch=master https://github.com/tabilab-dip/BOUN-PARS.git bpars
rm -rf ./bpars/.git
mv bpars/* .
rm -rf ./bpars
```

* Parser only runs in verbose mode. Need to make it switchable when deploying. (TODO)

## Run as a server

* Here are the commands to run the flask server:
    * Loading of the modules might take a few minutes. The server won't answer by that time
```
python.py api.py

in another terminal:
    curl -X POST -H "Content-Type: application/json" -d '{"query": "bu örnek bir cümledir."}' http://127.0.0.1:5000/evaluate

```


## Python evaluate

* Example python use of trained model
```python
import evaluate
# wait a few minutes, modules take some time to init
result = evaluate.parse_plaintext("bu örnek bir cümledir.")
print(result)

# ...
```

* Initial import takes some time, consequent parsings don't.

## Parse CoNLL-U File


```python
import evaluate
# wait a few minutes, modules take some time to init
with open("some_conllu_file.conllu", "r") as f:
    conllu_text = f.read()
result = evaluate.parse_conllu(conllu_text)
print(result)
```


BOUN-Pars is developed by Şaziye Betül Özateş, Arzucan Özgür, Tunga Güngör from the Department of Computer Engineering, and Balkız Öztürk from the Department of Linguistics, at Bogazici University. 

Please cite the following papers if you make use of this tool:

```
@article{ozates2020hybrid,
         author ={Şaziye Betül Özateş,  Arzucan Özgür, Tunga Güngör, Balkız Öztürk},
         title ={A Hybrid Approach to Dependency Parsing: Combining Rules and Morphology with Deep Learning},
         journal ={Under Review}}
```
