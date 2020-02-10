The Boun Morphological Disambiguator:
This program (md.pl) implements an averaged perceptron based morphological disambiguation system for Turkish text.
You can find the most up to date version at http://www.cmpe.boun.edu.tr/~hasim.

Please see the "Attribution Info" section for the methodology.
Please note that this implementation is a little bit different than the one described in the paper.
Main differences:
-The disambiguation corpus has been converted to the Boun morphological parser format.
-The feature set is different.
-The baseline model is no longer used and the disambiguation is done using Viterbi decoding.

Data Set:
The original morphological disambiguation data set is from Kemal Oflazer and Deniz Yüret. This data set of about 50K sentences was converted automatically to our parser format and splitted to:
-data.train.txt: 45K sentences training set
-data.dev.txt: 2.5K sentences development set
-data.test.txt: 2.5K sentences test set
-data.hand.txt: 958 tokens hand-labeled test set

Note that it is reported that the original corpus has been semi-automatically tagged, and our observation is that it is not very accurate.

Training and Testing:
md.pl(ver. 2.0): perl script that implements the disambiguator.
This version works with the Boun morphological parser output.
To train with the train set and test on the development set:
md.pl -train data.train.txt data.dev.txt model.txt
1. iter: 96.5401004897284
2. iter: 96.8793063240688
3. iter: 96.883546396998
4. iter: 96.9662278191185

To test the model on the test set:
md.pl -test model.txt data.test.txt
accuracy = 97.0514586202579

To test the model on the small hand-labeled test set:
md.pl -test model.txt data.hand.txt
accuracy = 96.4509394572025

To disambiguate a given data set using the model:
md.pl -disamb model[in] amb_set[in] unamb_set[out]

You should have your data set parsed by the Boun morphological parser (available at http://www.cmpe.boun.edu.tr/~hasim) to use the disambiguator with your text.

License:
The Boun Morphological Disambiguator is distributed under the Attribution-Noncommercial-Share Alike license.
A human-readable summary of the Legal Code is as follows:
Attribution — You must attribute the work in the manner specified by the author or licensor.
Noncommercial — You may not use this work for commercial purposes.
Share Alike — If you alter, transform, or build upon this work, you may distribute the resulting work only under the same or similar license to this one.
For the full license, see http://creativecommons.org/licenses/by-nc-sa/3.0/.

Attribution Info:
Please cite the following paper if you make use of this resource in your research.

Haşim Sak, Tunga Güngör, and Murat Saraçlar. Morphological disambiguation of Turkish text with perceptron algorithm.
In CICLing 2007, volume LNCS 4394, pages 107-118, 2007.

BibTeX entry:
@inproceedings{sak-et-al-cicling-07,
	Author = {Ha{\c s}im Sak and Tunga G{\"u}ng{\"o}r and Murat Sara{\c c}lar},
	Booktitle = {CICLing 2007},
	Pages = {107--118},
	Title = {Morphological Disambiguation of {Turkish} Text with Perceptron Algorithm},
	Volume = {LNCS 4394},
	Year = {2007},
	Url = {http://www.cmpe.boun.edu.tr/~hasim/papers/CICLing07.pdf}}

Contact Info:
Haşim Sak
Department of Computer Engineering
Boğaziçi University
34342 Bebek, İstanbul, Turkey
hasim.sak@gmail.com
hasim.sak@boun.edu.tr

May 27, 2009
