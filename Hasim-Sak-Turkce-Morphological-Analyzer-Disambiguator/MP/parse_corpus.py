#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Hasim Sak
#Description: An example python script to use the stochastic morphological parser for Turkish.

import sys
import re
import TurkishMorphology

if len(sys.argv) < 2:
	print('usage:', sys.argv[0], 'corpus[ex:test.txt]')
	exit(1)

def parse_corpus():
	TurkishMorphology.load_lexicon('turkish.fst');
	n = 0
	e = 0
	f = open(sys.argv[1], 'r')
	for line in f:
		print('<S> <S>+BSTag')
		line = line.rstrip()
		words = re.split('\s+', line)
		for w in words:
			parses = TurkishMorphology.parse(w)
			if not parses:
				print(w, w+"[Unknown]")
				continue
			print(w),
			for p in parses: #There may be more than one possible morphological analyses for a word
				(parse, neglogprob) = p #An estimated negative log probability for a morphological analysis is also returned
				print(parse),
			print
		print('</S> </S>+ESTag')
	f.close()

parse_corpus()
