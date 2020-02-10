#!/bin/bash
#



echo "$1" | python3 full_pipeline_stream.py --gpu -1 --conf models_tr_imst/pipelines.yaml parse_plaintext > input.conllu

csplit --digits=1  --quiet --prefix=infile input.conllu "/# newdoc/+1" "{*}"
python3 ./morp-based-model/add_morp_analysis_to_conllu.py infile1 input-text.txt
cd Hasim-Sak-Turkce-Morphological-Analyzer-Disambiguator/MP/
python2 parse_corpus.py ../../input-text.txt > ../../input-text-parsed.txt
cd ..
cd MD-2.0
perl md.pl -disamb model.txt ../../input-text-parsed.txt ../../input-text-parsed-disamb.txt
cd ..
cd ..
sed -i '1d' input-text-parsed-disamb.txt
sed -i '$ d' input-text-parsed-disamb.txt
python3 ./morp-based-model/add_morpheme_to_conllu.py infile1 input-text-parsed-disamb.txt input-fullmorphed.conllu full
python3 ./rule-based-model/rule_based_parser.py input-fullmorphed.conllu
python3 ./morp-based-model/add_morpheme_to_conllu.py ruled-input-fullmorphed.conllu input-text-parsed-disamb.txt input-morphed-ruled.conllu last

python3 ./Parser-hybrid/main.py --save_dir ./Parser-hybrid/saves/model_tr_imst_ruled_morphed_new_1 parse ./input-morphed-ruled.conllu --output_dir ./ --output_file  morphed-ruled-new-1_input-morphed-ruled_output.conllu

python3 ./restore_conllu_lines.py morphed-ruled-new-1_input-morphed-ruled_output.conllu infile1

rm infile0 input-text.txt input-text-parsed.txt input-text-parsed-disamb.txt input-fullmorphed.conllu ruled-input-fullmorphed.conllu input-morphed-ruled.conllu morphed-ruled-new-1_input-morphed-ruled_output.conllu

mv infile1 input.conllu
