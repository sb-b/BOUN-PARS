#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Timothy Dozat
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.





import sys
import os
import re
import argparse
import codecs
from backports import lzma

import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt
from collections import Counter

#***************************************************************
if __name__ == '__main__':
  """ """
  
  parser = argparse.ArgumentParser()
  parser.add_argument('-k', '--k_trials', type=int, default=100)
  parser.add_argument('-n', '--n_words', type=int, default=5000)
  parser.add_argument('files', nargs='+')
  
  args = parser.parse_args()
  type_counter = Counter()
  for filename in args.files:
    with codecs.open(filename, encoding='utf-8', errors='ignore') as f:
      for line in f:
        line = line.strip()
        if line:
          if not re.match('#|[0-9]+[-.][0-9]+', line):
            type_counter[line.split('\t')[1]] += 1
  
  types = list(type_counter.keys())
  total = sum(type_counter.values())
  probs = [type_counter[type_] / total for type_ in types]
  
  trials = []
  n_words = min(args.n_words, len(types)) or len(types)
  for _ in range(args.k_trials):
    chosen_types = np.random.choice(types, size=n_words, replace=False, p=probs)
    with codecs.open('uncompressed.txt', 'w', encoding='utf-8', errors='ignore') as f:
      f.write('\n'.join(chosen_types))
    with lzma.open('compressed.txt.xz', 'wb') as f:
      f.write('\n'.join(chosen_types).encode('utf-8', 'ignore'))
    trials.append(os.path.getsize('compressed.txt.xz')/os.path.getsize('uncompressed.txt'))
  os.remove('uncompressed.txt')
  os.remove('compressed.txt.xz')
  print(np.mean(trials),file=sys.stderr)
