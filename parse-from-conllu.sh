#!/bin/bash
#


python3 ./morp-based-model/conllu_to_morp_addition.py $1 input-text.txt
cd Hasim-Sak-Turkce-Morphological-Analyzer-Disambiguator/MP/
python2 parse_corpus.py ../../input-text.txt > ../../input-text-parsed.txt
cd ..
cd MD-2.0
perl md.pl -disamb model.txt ../../input-text-parsed.txt ../../input-text-parsed-disamb.txt
cd ..
cd ..
sed -i '1d' input-text-parsed-disamb.txt
sed -i '$ d' input-text-parsed-disamb.txt
python3 ./morp-based-model/add_morp_to_conllu.py $1 input-text-parsed-disamb.txt input-fullmorphed.conllu full
python3 ./rule-based-model/rule_based_parser_tags_ablation.py input-fullmorphed.conllu
python3 ./morp-based-model/add_morp_to_conllu.py ruled-input-fullmorphed.conllu input-text-parsed-disamb.txt input-morphed-ruled.conllu last

python3 ./Parser-hybrid/main.py --save_dir ./Parser-hybrid/saves/model_tr_imst_ruled_morphed_new_1 parse ./input-morphed-ruled.conllu --output_dir ./ --output_file  $2

rm input-text.txt input-text-parsed.txt input-text-parsed-disamb.txt input-fullmorphed.conllu ruled-input-fullmorphed.conllu


