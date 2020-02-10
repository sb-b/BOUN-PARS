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
import re
import codecs
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from nparser.misc.colors import ctext, color_pattern
from nparser.neural.models.nn import NN

#***************************************************************
class BaseXTagger(NN):
  """ """
  
  PAD = 0
  ROOT = 1
  
  #=============================================================
  def __call__(self, vocabs, moving_params=None):
    """ """
    
    self.moving_params = moving_params
    if isinstance(vocabs, dict):
      self.vocabs = vocabs
    else:
      self.vocabs = {vocab.name: vocab for vocab in vocabs}
    
    input_vocabs = [self.vocabs[name] for name in self.input_vocabs]
    embed = self.embed_concat(input_vocabs)
    for vocab in list(self.vocabs.values()):
      if vocab not in input_vocabs:
        vocab.generate_placeholder()
    placeholder = self.vocabs['words'].placeholder
    if len(placeholder.get_shape().as_list()) == 3:
      placeholder = placeholder[:,:,0]
    self._tokens_to_keep = tf.to_float(tf.greater(placeholder, self.ROOT))
    self._batch_size = tf.shape(placeholder)[0]
    self._bucket_size = tf.shape(placeholder)[1]
    self._sequence_lengths = tf.reduce_sum(tf.to_int32(tf.greater(placeholder, self.PAD)), axis=1)
    self._n_tokens = tf.to_int32(tf.reduce_sum(self.tokens_to_keep))
    
    top_recur = embed
    for i in range(self.n_layers):
      with tf.variable_scope('RNN%d' % i):
        top_recur, _ = self.RNN(top_recur, self.recur_size)
    return top_recur
  
  #=============================================================
  def process_accumulators(self, accumulators, time=None):
    """ """
    
    n_tokens, n_seqs, loss, corr, xcorr, seq_corr = accumulators
    acc_dict = {
      'Loss': loss,
      'TS': corr/n_tokens*100,
      'XTS': xcorr/n_tokens*100,
      'SS': seq_corr/n_seqs*100,
    }
    if time is not None:
      acc_dict.update({
        'Token_rate': n_tokens / time,
        'Seq_rate': n_seqs / time,
      })
    return acc_dict
  
  #=============================================================
  def update_history(self, history, accumulators):
    """ """
    
    acc_dict = self.process_accumulators(accumulators)
    for key, value in acc_dict.items():
      history[key].append(value)
    return history['TS'][-1]
  
  #=============================================================
  def print_accuracy(self, accumulators, time, prefix='Train'):
    """ """
    
    acc_dict = self.process_accumulators(accumulators, time=time)
    strings = []
    strings.append(color_pattern('Loss:', '{Loss:7.3f}', 'bright_red'))
    strings.append(color_pattern('TS:', '{TS:5.2f}%', 'bright_cyan'))
    strings.append(color_pattern('XTS:', '{XTS:5.2f}%', 'bright_cyan'))
    strings.append(color_pattern('SS:', '{SS:5.2f}%', 'bright_green'))
    strings.append(color_pattern('Speed:', '{Seq_rate:6.1f} seqs/sec', 'bright_magenta'))
    string = ctext('{0}  ', 'bold') + ' | '.join(strings)
    print(string.format(prefix, **acc_dict),file=sys.stderr)
    return
  
  #=============================================================
  def plot(self, history, prefix='Train'):
    """ """
    
    pass
  
  #=============================================================
  def check(self, preds, sents, fileobj):
    """ """

    for tokens, preds, xpreds in zip(sents, preds[0], preds[1]):
      for token, pred, xpred in zip(list(zip(*tokens)), preds, xpreds):
        tag = self.vocabs['tags'][pred]
        xtag = self.vocabs['xtags'][xpred]
        fileobj.write('\t'.join(token+(tag, xtag))+'\n')
      fileobj.write('\n')
    return

  #=============================================================
  def write_probs(self, sents, output_file, probs, inv_idxs, metadata):
    """
    `output_file` can be a string or an open file (latter will be flushed but not closed)
    """
    
    # Turns list of tuples of tensors into list of matrices
    tag_probs = [tag_prob for batch in probs for tag_prob in batch[0]]
    xtag_probs = [xtag_prob for batch in probs for xtag_prob in batch[1]]
    tokens_to_keep = [weight for batch in probs for weight in batch[2]]
    tokens = [sent for batch in sents for sent in batch]

    close_out=False
    if isinstance(output_file,str):
      f=codecs.open(output_file, 'w', encoding='utf-8', errors='ignore')
      close_out=True
    else:
      f=output_file
    for meta_idx,i in enumerate(inv_idxs):
      sent, tag_prob, xtag_prob, weights = tokens[i], tag_probs[i], xtag_probs[i], tokens_to_keep[i]
      sent = list(zip(*sent))
      xtag_prob[:,self.vocabs['xtags']["UNK"]]=0.0 ## this masks UNK class probability and prevents Xtagger to produce unknown output (if input has min_occur_count set to 2 the tagger learns to predict unknown...)
      tag_preds = np.argmax(tag_prob, axis=1)
      xtag_preds = np.argmax(xtag_prob, axis=1)
      sent_meta=metadata[meta_idx]
      if sent_meta["comments"]:
        if "Parserv2dummysentenceJHYSTGSH" in sent_meta["comments"][0]:
          continue
        f.write("\n".join(sent_meta["comments"]))
        f.write("\n")
      for tok_idx,(token, tag_pred, xtag_pred, weight) in enumerate(zip(sent, tag_preds[1:], xtag_preds[1:], weights[1:])):
        for b,e,form in sent_meta["multiwordtokens"]:
            if tok_idx+1==b: #there goes a multiword right here!
              f.write("{}-{}\t{}".format(b,e,form))
              f.write("\t_"*8)
              f.write("\n")
        token = list(token)
        token.insert(5, sent_meta["feats"][tok_idx])
        token.append('_')
        token.append(sent_meta["miscfield"][tok_idx])
        token[3] = self.vocabs['tags'][tag_pred]
        token[4] = self.vocabs['xtags'][xtag_pred]
        f.write('\t'.join(token)+'\n')
      if sent: #WHY DO I NEED THIS? CAN THERE BE AN EMPTY SENTENCE?
        f.write('\n')
    f.flush()
    if close_out:
      f.close()
    return
  
  #=============================================================
  @property
  def train_keys(self):
    return ('n_tokens', 'n_seqs', 'loss', 'n_tag_correct', 'n_xtag_correct', 'n_seqs_correct')
  
  #=============================================================
  @property
  def valid_keys(self):
    return ('tag_preds', 'xtag_preds')

  #=============================================================
  @property
  def parse_keys(self):
    return ('tag_probs', 'xtag_probs', 'tokens_to_keep')
