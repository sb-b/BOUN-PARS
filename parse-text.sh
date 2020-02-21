#!/bin/bash


echo "$1" | /usr/bin/python3.5 full_pipeline_stream.py --gpu -1 --conf model_tr_imst_ruled_morphed_pipeline/pipelines.yaml tokenize > input_tokenized.conllu

python3 ./morp-based-model/add_morp_analysis_to_conllu.py input_tokenized.conllu input-text.txt

cd Hasim-Sak-Turkce-Morphological-Analyzer-Disambiguator/MP/

python2 parse_corpus.py ../../input-text.txt > ../../input-text-parsed.txt

cd ..
cd MD-2.0

perl md.pl -disamb model.txt ../../input-text-parsed.txt ../../input-text-parsed-disamb.txt

cd ..
cd ..

sed -i '1d' input-text-parsed-disamb.txt
sed -i '$ d' input-text-parsed-disamb.txt

python3 ./morp-based-model/add_morpheme_to_conllu.py input_tokenized.conllu input-text-parsed-disamb.txt input-fullmorphed.conllu full
python3 ./rule-based-model/rule_based_parser.py input-fullmorphed.conllu
python3 ./morp-based-model/add_morpheme_to_conllu.py ruled-input-fullmorphed.conllu input-text-parsed-disamb.txt input-morphed-ruled.conllu last

cat input-morphed-ruled.conllu | /usr/bin/python3.5 full_pipeline_stream.py --gpu -1 --conf model_tr_imst_ruled_morphed_pipeline/pipelines.yaml my_parse_conllu > output-morphed-ruled.conllu

sed -i '1,2d' output-morphed-ruled.conllu

python3 ./restore_conllu_lines.py output-morphed-ruled.conllu input_tokenized.conllu
cat final_output.conllu

rm input_tokenized.conllu input-text.txt input-text-parsed.txt input-text-parsed-disamb.txt input-fullmorphed.conllu input-morphed-ruled.conllu ruled-input-fullmorphed.conllu output-morphed-ruled.conllu final_output.conllu


