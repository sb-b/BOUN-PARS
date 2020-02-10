This program implements an averaged perceptron based morphological disambiguation system for Turkish text.
You can find the most up to date version at http://www.cmpe.boun.edu.tr/~hasim.
The method is described in the following paper.
Haşim Sak, Tunga Güngör, and Murat Saraçlar. Morphological disambiguation of Turkish text with perceptron algorithm.
In CICLing 2007, volume LNCS 4394, pages 107-118, 2007.
If you want to use this program in your research, please cite this paper.
Please note that this implementation is a little bit different than the one described in the paper.
The difference is that the baseline model is no longer used and the disambiguation is done using Viterbi decoding.
This results in improved accuracy.

train.merge: Morphological disambiguation data set from Kemal Oflazer and Deniz Yüret. This data set of about 50K sentences was splitted to:
-data.train.txt: 45K sentences training set
-data.dev.txt: 2.5K sentences development set
-data.test.txt: 2.5K sentences test set
It is reported that this data set has been semi-automatically tagged, and our observation is it is not very accurate.
test.merge: 959 tokens hand-labeled data set

md.pl: perl script that implements the disambiguator.
To train with the train set and test on the development set:
md.pl -train data.train.txt data.dev.txt model.txt
1. iter: 97.5951759948314
2. iter: 97.7746404728291
3. iter: 97.834461965495
4. iter: 97.8703548610945

To test the model on the test set:
md.pl -test model.txt data.test.txt 
accuracy = 97.8126765869279

To test the model on the small hand-labeled test set:
md.pl -test model.txt test.merge
accuracy = 96.4037122969838

To disambiguate a given data set using the model:
md.pl -disamb model[in] amb_set[in] unamb_set[out]

You should have your data set parsed by Kemal Oflazer's morphological parser to use the disambiguator.

Contact Info:
Haşim Sak
Department of Computer Engineering
Boğaziçi University
34342 Bebek, İstanbul, Turkey
hasim.sak@gmail.com

August 17, 2007
