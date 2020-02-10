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
import io
import re
import codecs
from collections import Counter

import numpy as np
import tensorflow as tf

from nparser import Configurable, Multibucket
from nparser.vocabs.base_vocab import BaseVocab
from nparser.misc.bucketer import Bucketer

__all__ = ['Trainset', 'Parseset']

#***************************************************************
class Dataset(Configurable):
  """ """
  
  #=============================================================
  def __init__(self, vocabs, *args, **kwargs):
    """ """
    
    nlp_model = kwargs.pop('nlp_model', None)
    if "parse_files" in kwargs and isinstance(kwargs["parse_files"],io.StringIO): ### SPECIAL CASE - PARSING StringIO
      self.preopen_parse_file=kwargs.pop("parse_files") #This doesn't really play well with the configparser thing
    else:
      self.preopen_parse_file=None
    super(Dataset, self).__init__(*args, **kwargs)
    
    self._vocabs = vocabs
    self._multibuckets = [Multibucket.from_configurable(vocab, name='%s-%s'%(self.name, vocab.name)) for vocab in self.vocabs]
    self._metadata=[]
    
    if nlp_model is not None:
      self._nlp_model = nlp_model.from_configurable(self, name=self.name)
    else:
      self._nlp_model = None
    
    with Bucketer.from_configurable(self, self.n_buckets, name='bucketer-%s'%self.name) as bucketer:
      splits = bucketer.compute_splits(len(sent) for sent,metadata in self.iterfiles())
      
      for i in range(len(splits)):
        splits[i] += 1
    for multibucket, vocab in self.iteritems():
      multibucket.open(splits, depth=vocab.depth)
    for sent,metadata in self.iterfiles():
     
      #mycode begins
      #words = [line[1] for line in sent]
      #uposList = [line[3] for line in sent]
      #xposList = [line[4].split('|',1)[0][5:] for line in sent]
      #morpList = [line[5] for line in sent]
      #newUposList = rule_based_parser(words,uposList,xposList,morpList)
      #for i,line in enumerate(sent):
       #  line[3] = newUposList[i]
      #print(sent)
      #mycode ends
    
      self._metadata.append(metadata)
      for multibucket, vocab in self.iteritems():
        tokens = [line[vocab.conll_idx] for line in sent]
 
        idxs = [vocab.ROOT] + [vocab.index(token) for token in tokens]

        multibucket.add(idxs, tokens)
    for multibucket in self:
      multibucket.close()
    self._multibucket = Multibucket.from_dataset(self)
    
    return
  
  #=============================================================
  def __call__(self, moving_params=None):
    """ """
    
    return self._nlp_model(self.vocabs, moving_params=moving_params)
  
  #=============================================================
  def iterfiles(self):
    """ """
    #0 1    2     3     4     5     6    7     8     9
    ID,FORM,LEMMA,UPOS,XPOS,FEATS,HEAD,DEPREL,DEPS,MISC=range(10)
    if isinstance(self.preopen_parse_file,io.StringIO): #Go from here
      data_files=[self.preopen_parse_file]
    else:
      data_files=self.data_files
    for data_file in data_files:
      if isinstance(data_file,str):
        f=codecs.open(data_file, encoding='utf-8', errors='ignore')
      else:
        f=data_file
        
      buff = []
      metadata = {"comments":[],"miscfield":[],"feats":[],"multiwordtokens":[]}
      for line in f:
        line = line.strip()
        if line:
          if not line.startswith('#'):
            if not re.match('^[0-9]+[-.][0-9]+\t', line):
              cols=line.split("\t")
              metadata["miscfield"].append(cols[MISC])
              metadata["feats"].append(cols[FEATS])
              buff.append(cols)
            elif re.match('^[0-9]+[-][0-9]+\t', line): #multiword token
              cols=line.split("\t")
              beg,end=cols[ID].split("-")
              metadata["multiwordtokens"].append((int(beg),int(end),cols[FORM]))
          else:
            metadata["comments"].append(line)
        elif buff:
          yield buff, metadata
          buff = []
          metadata = {"comments":[],"miscfield":[],"feats":[],"multiwordtokens":[]}
      yield buff, metadata

      if isinstance(data_file,str):
        f.close()
      else:
        f.seek(0) #rewind for new reading
  
  #=============================================================
  def iterbatches(self, shuffle=True, return_check=False):
    """ """
    
    batch_size = self.batch_size
    batch_by = self.batch_by 
    batches = []
    for bkt_idx, bucket in enumerate(self.multibucket):
      if batch_size == 0:
        n_splits = 1
      else:
        if batch_by == 'tokens':
          n_tokens = bucket.indices.shape[0] * bucket.indices.shape[1]
          n_splits = max(n_tokens // batch_size, 1)
        elif batch_by == 'seqs':
          n_seqs = bucket.indices.shape[0]
          n_splits = max(n_seqs // batch_size, 1)
      if shuffle:
        range_func = np.random.permutation
      else:
        range_func = np.arange
      splits = np.array_split(range_func(bucket.indices.shape[0])[1:], n_splits)
      for split in splits:
        batches.append( (bkt_idx, split) )
    if shuffle:
      np.random.shuffle(batches)

    for bkt_idx, batch in batches:
      feed_dict = {}
      tokens = []
      for multibucket, vocab in self.iteritems():
        bucket = multibucket[bkt_idx]
        indices = bucket.indices[batch]
        vocab.set_feed_dict(indices, feed_dict)
        if return_check:
          #print("INDICES",indices.shape,indices)
          if len(indices.shape) == 2:
            tokens.append(vocab[indices])
          elif len(indices.shape) == 3:
            for i,subvocab in enumerate(vocab):
              tokens.append(subvocab[indices[:,:,i]])
              #print("SUBVOCAB",subvocab)
            #tokens.extend([subvocab[indices[:,:,i]] for i, subvocab in enumerate(vocab)])
            # TODO This is super hacky
            if hasattr(subvocab, 'idx2tok'):
              tokens[-1] = [[subvocab.idx2tok.get(idx, subvocab[subvocab.PAD]) for idx in idxs] for idxs in indices[:,:,-1]]
        elif not shuffle:
          tokens.append(bucket.get_tokens(batch))

      if not shuffle or return_check:
        yield feed_dict, list(zip(*tokens))
      else:
        yield feed_dict
  
  #=============================================================
  def iteritems(self):
    for i in range(len(self)):
      yield (self[i], self._vocabs[i])
  
  #=============================================================
  def update_history(self, history, accumulators):
    return self._nlp_model.update_history(history, accumulators)
  
  def print_accuracy(self, accumulators, time):
    return self._nlp_model.print_accuracy(accumulators, time, prefix=self.PREFIX.title())
  
  def write_probs(self, sents, output_file, probs, metadata):
    return self._nlp_model.write_probs(sents, output_file, probs, self.multibucket.inv_idxs(), metadata)

  def check(self, preds, sents, fileobj):
    return self._nlp_model.check(preds, sents, fileobj)
  
  def plot(self, history):
    return self._nlp_model.plot(history)
  
  #=============================================================
  @property
  def data_files(self):
    return getattr(self, '{0}_files'.format(self.PREFIX.lower()))
  @property
  def multibucket(self):
    return self._multibucket
  @property
  def vocabs(self):
    return self._vocabs
  @property
  def train_keys(self):
    return self._nlp_model.train_keys
  @property
  def valid_keys(self):
    return self._nlp_model.valid_keys
  @property
  def parse_keys(self):
    return self._nlp_model.parse_keys
  
  #=============================================================
  def __len__(self):
    return len(self._multibuckets)
  def __iter__(self):
    return (multibucket for multibucket in self._multibuckets)
  def __getitem__(self, key):
    return self._multibuckets[key]

#***************************************************************
class Trainset(Dataset):
  PREFIX = 'train'
class Parseset(Dataset):
  PREFIX = 'parse'

#***************************************************************
if __name__ == '__main__':
  """ """
  
  from nparser.vocabs import *
  from nparser.dataset import Trainset
  
  configurable = Configurable()
  dep_vocab = DepVocab.from_configurable(configurable)
  word_vocab = WordVocab.from_configurable(configurable)
  lemma_vocab = LemmaVocab.from_configurable(configurable)
  pretrained_vocab = PretrainedVocab.from_vocab(word_vocab)
  char_vocab = NgramMultivocab.from_vocab(word_vocab)
  word_multivocab = Multivocab.from_configurable(configurable, [word_vocab, pretrained_vocab, char_vocab], name='words')
  tag_vocab = TagVocab.from_configurable(configurable)
  xtag_vocab = XTagVocab.from_configurable(configurable)
  head_vocab = HeadVocab.from_configurable(configurable)
  rel_vocab = RelVocab.from_configurable(configurable)
  trainset = Trainset.from_configurable(configurable, [dep_vocab, word_multivocab, lemma_vocab, tag_vocab, xtag_vocab, head_vocab, rel_vocab])
  trainset()
  print('Dataset passes',file=sys.stderr)
  
