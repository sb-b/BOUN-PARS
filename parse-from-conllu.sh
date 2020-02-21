#!/bin/bash
#


python3 ./morp-based-model/add_morp_analysis_to_conllu.py $1 input-text.txt

cd Hasim-Sak-Turkce-Morphological-Analyzer-Disambiguator/MP/

echo "Morphological analysis is being performed..."

python2 parse_corpus.py ../../input-text.txt > ../../input-text-parsed.txt

cd ..
cd MD-2.0

perl md.pl -disamb model.txt ../../input-text-parsed.txt ../../input-text-parsed-disamb.txt

cd ..
cd ..

sed -i '1d' input-text-parsed-disamb.txt
sed -i '$ d' input-text-parsed-disamb.txt

python3 ./morp-based-model/add_morpheme_to_conllu.py $1 input-text-parsed-disamb.txt input-fullmorphed.conllu full

echo "Morphological analysis is done."
echo "Rule-based parsing is being performed..."

python3 ./rule-based-model/rule_based_parser.py input-fullmorphed.conllu

echo "Rule-based parsing is done."

python3 ./morp-based-model/add_morpheme_to_conllu.py ruled-input-fullmorphed.conllu input-text-parsed-disamb.txt input-morphed-ruled.conllu last

echo "Input file is being parsed..."

python3 ./Parser-hybrid/main.py --save_dir ./Parser-hybrid/saves/model_tr_imst_ruled_morphed_new_1 parse ./input-morphed-ruled.conllu --output_dir ./ --output_file  $2

python3 ./restore_conllu_lines.py $2 $1

mv final_output.conllu $2

rm input-text.txt input-text-parsed.txt input-text-parsed-disamb.txt input-fullmorphed.conllu ruled-input-fullmorphed.conllu input-morphed-ruled.conllu


