
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
import gc
import os
import time
import codecs
import pickle as pkl
from collections import defaultdict
import os.path as op

import numpy as np
import tensorflow as tf

from nparser import Configurable
from nparser.vocabs import *
from nparser.dataset import *
from nparser.misc.colors import ctext
from nparser.neural.optimizers import RadamOptimizer



import types


import io
import select
from keras import backend as K
K.set_image_dim_ordering('th')

#***************************************************************
class Network(Configurable):
  """ """
  
  #=============================================================
  def __init__(self, *args, **kwargs):
    """ """
    
    super(Network, self).__init__(*args, **kwargs)
    # hacky!
    #hacky_train_files = op.join(self.save_dir, op.basename(self.get("train_files")))
    #self._config.set('Configurable', 'train_files', hacky_train_files)
    
    # TODO make this more flexible, maybe specify it in config?
    
    temp_nlp_model = self.nlp_model.from_configurable(self)
    
    if temp_nlp_model.input_vocabs == ['tags']:
      
      word_vocab = WordVocab.from_configurable(self)
      
      word_multivocab = Multivocab.from_configurable(self, [word_vocab], name=word_vocab.name)
      
      tag_vocab = TagVocab.from_configurable(self, initialize_zero=False)
    else:
      
      word_vocab = WordVocab.from_configurable(self)

      pretrained_vocab = PretrainedVocab.from_vocab(word_vocab)
      
      subtoken_vocab = self.subtoken_vocab.from_vocab(word_vocab)

      #mycode
      morp_vocab = MorpVocab.from_configurable(self) 
      rule_vocab = RuleVocab.from_configurable(self) 
      #mycode
      
      word_multivocab = Multivocab.from_configurable(self, [word_vocab, pretrained_vocab, subtoken_vocab], name=word_vocab.name)
   
      #mycode
      #word_multivocab = Multivocab.from_configurable(self, [word_vocab, pretrained_vocab, subtoken_vocab, rule_vocab], name=word_vocab.name)
      #print("multivocab: " ,word_multivocab)
      #mycode

      #word_multivocab = Multivocab.from_configurable(self, [word_vocab, pretrained_vocab], name=word_vocab.name)
      tag_vocab = TagVocab.from_configurable(self)
    
    dep_vocab = DepVocab.from_configurable(self)
    lemma_vocab = LemmaVocab.from_configurable(self)
    xtag_vocab = XTagVocab.from_configurable(self)
    head_vocab = HeadVocab.from_configurable(self)
    rel_vocab = RelVocab.from_configurable(self)
    self._vocabs = [dep_vocab, word_multivocab, lemma_vocab, tag_vocab, xtag_vocab, head_vocab, rel_vocab, morp_vocab, rule_vocab]
    self._global_step = tf.Variable(0., trainable=False, name='global_step')
    self._global_epoch = tf.Variable(0., trainable=False, name='global_epoch')
    self._optimizer = RadamOptimizer.from_configurable(self, global_step=self.global_step)
    return
  
  #=============================================================
  def add_file_vocabs(self, conll_files):
    """ """
    
    # TODO don't depend on hasattr
    for vocab in self.vocabs:
      if hasattr(vocab, 'add_files'):
        vocab.add_files(conll_files)
    for vocab in self.vocabs:
      if hasattr(vocab, 'index_tokens'):
        vocab.index_tokens()
    return
  
  #=============================================================
  def setup_vocabs(self):
    """ """
    
    for vocab in self.vocabs:
      vocab.setup()
    return 
  
  #=============================================================
  def train(self, load=False):
    """ """
    
    # prep the configurables

    self.add_file_vocabs(self.parse_files)
    self.setup_vocabs()
    trainset = Trainset.from_configurable(self, self.vocabs, nlp_model=self.nlp_model)
    with tf.variable_scope(self.name.title()):
      train_tensors = trainset()
    print("train_tensors: ", train_tensors)
    train = self.optimizer(tf.losses.get_total_loss())
    train_outputs = [train_tensors[train_key] for train_key in trainset.train_keys]
    saver = tf.train.Saver(self.save_vars, max_to_keep=1)
    validset = Parseset.from_configurable(self, self.vocabs, nlp_model=self.nlp_model)
    with tf.variable_scope(self.name.title(), reuse=True):
      valid_tensors = validset(moving_params=self.optimizer)
    valid_outputs = [valid_tensors[train_key] for train_key in validset.train_keys]
    valid_outputs2 = [valid_tensors[valid_key] for valid_key in validset.valid_keys]
    current_acc = 0
    best_acc = 0
    n_iters_since_improvement = 0
    n_iters_in_epoch = 0
    
    # calling these properties is inefficient so we save them in separate variables
    min_train_iters = self.min_train_iters
    max_train_iters = self.max_train_iters
    validate_every = self.validate_every
    save_every = self.save_every
    verbose = self.verbose
    quit_after_n_iters_without_improvement = self.quit_after_n_iters_without_improvement
    
    # load or prep the history
    if load:
      self.history = pkl.load(open(os.path.join(self.save_dir, 'history.pkl')))
    else:
      self.history = {'train': defaultdict(list), 'valid': defaultdict(list)}
    
    # start up the session
    config_proto = tf.ConfigProto()
    #if self.per_process_gpu_memory_fraction == -1:
    config_proto.gpu_options.allow_growth = True
    #else:
    #  config_proto.gpu_options.per_process_gpu_memory_fraction = self.per_process_gpu_memory_fraction
    with tf.Session(config=config_proto) as sess:
      sess.run(tf.global_variables_initializer())
      if load:
        saver.restore(sess, tf.train.latest_checkpoint(self.save_dir))
      total_train_iters = sess.run(self.global_step)
      train_accumulators = np.zeros(len(train_outputs))
      train_time = 0
      # training loop
      while total_train_iters < max_train_iters:
        print(total_train_iters)
        for feed_dict in trainset.iterbatches():
         # print("feed_dict: ",feed_dict)
          start_time = time.time()
          batch_values = sess.run(train_outputs + [train], feed_dict=feed_dict)[:-1]
          batch_time = time.time() - start_time
          # update accumulators
          total_train_iters += 1
          n_iters_since_improvement += 1
          train_accumulators += batch_values
          train_time += batch_time
          # possibly validate
          if total_train_iters == 1 or (total_train_iters % validate_every == 0):
            valid_accumulators = np.zeros(len(train_outputs))
            valid_time = 0
            with codecs.open(os.path.join(self.save_dir, 'sanity_check'), 'w', encoding='utf-8', errors='ignore') as f:
              for feed_dict, sents in validset.iterbatches(return_check=True):
                #print("sent: ", sents[0])
                start_time = time.time()
                batch_values = sess.run(valid_outputs+valid_outputs2, feed_dict=feed_dict)
                batch_time = time.time() - start_time
                # update accumulators
                valid_accumulators += batch_values[:len(valid_outputs)]
                valid_preds = batch_values[len(valid_outputs):]
                valid_time += batch_time
                validset.check(valid_preds, sents, f)
            # update history
            trainset.update_history(self.history['train'], train_accumulators)
            current_acc = validset.update_history(self.history['valid'], valid_accumulators)
            # print
            if verbose:
              print(ctext('{0:6d}'.format(int(total_train_iters)), 'bold')+')') 
              sys.stdout.flush()
              trainset.print_accuracy(train_accumulators, train_time)
              validset.print_accuracy(valid_accumulators, valid_time)
            train_accumulators = np.zeros(len(train_outputs))
            train_time = 0
            if current_acc > best_acc:
              if verbose:
                print(ctext('Saving model...', 'bright_yellow'),file=sys.stderr)
                sys.stderr.flush() 
              best_acc = current_acc
              n_iters_since_improvement = 0
              saver.save(sess, os.path.join(self.save_dir, self.name.lower()),
                         #global_step=self.global_epoch,
                         write_meta_graph=False)
              with open(os.path.join(self.save_dir, 'history.pkl'), 'wb') as f:
                pkl.dump(dict(self.history), f)
            elif n_iters_since_improvement >= quit_after_n_iters_without_improvement and total_train_iters > min_train_iters:
              break
        else:
          # We've completed one epoch
          if total_train_iters <= min_train_iters:
            saver.save(sess, os.path.join(self.save_dir, self.name.lower()),
                       #global_step=self.global_epoch,
                       write_meta_graph=False)
            with open(os.path.join(self.save_dir, 'history.pkl'), 'wb') as f:
              pkl.dump(dict(self.history), f)
          sess.run(self.global_epoch.assign_add(1.))
          continue
        break
      # Now parse the training and testing files
      input_files = self.train_files + self.parse_files
      saver.restore(sess, tf.train.latest_checkpoint(self.save_dir))
      for input_file in input_files:
        parseset = Parseset.from_configurable(self, self.vocabs, parse_files=input_file, nlp_model=self.nlp_model)
        with tf.variable_scope(self.name.title(), reuse=True):
          parse_tensors = parseset(moving_params=self.optimizer)
        parse_outputs = [parse_tensors[parse_key] for parse_key in parseset.parse_keys]

        input_dir, input_file = os.path.split(input_file)
        output_dir = self.save_dir
        output_file = input_file
        
        start_time = time.time()
        probs = []
        sents = []
        for feed_dict, tokens in parseset.iterbatches(shuffle=False):
          probs.append(sess.run(parse_outputs, feed_dict=feed_dict))
          sents.append(tokens)
        parseset.write_probs(sents, os.path.join(output_dir, output_file), probs, parseset._metadata)
    if self.verbose:
      print(ctext('Parsing {0} file(s) took {1} seconds'.format(len(input_files), time.time()-start_time), 'bright_green'),file=sys.stderr)
    return
  
  #=============================================================

  @classmethod
  def dummy_sents_hack(cls):
    """Make five dummy sentences of five lengths"""
    outp=[]
    for sent_len in range(5,16):
      outp.append("# Parserv2dummysentenceJHYSTGSH")
      for wrd in range(1,sent_len+1):
        outp.append("\t".join([str(wrd),"DUMMY","DUMMY","NOUN","NOUN","_",str(wrd-1),"nsubj","_","DUMMY"]))
      outp.append("")
    return "\n".join(outp)+"\n"
  
  @classmethod
  def nonblocking_batches(cls,f=sys.stdin,timeout=0.2,batch_lines=150000):
    """Yields batches of the input (as string), always ending with an empty line.
       Batch is formed when at least batch_lines are read, or when no input is seen in timeour seconds
       Stops yielding when f is closed"""
    dummies=cls.dummy_sents_hack()
    line_buffer=[]
    while True:
        ready_to_read=select.select([f], [], [], timeout)[0] #check whether f is ready to be read, wait at least timeout (otherwise we run a crazy fast loop)
        if not ready_to_read:
            # Stdin is not ready, yield what we've got, if anything
            if line_buffer:
                print("Yielding",len(list(line for line in line_buffer if line.startswith("1\t"))), file=sys.stderr)
                sys.stderr.flush()
                yield dummies+"".join(line_buffer)
                line_buffer=[]
            continue #next try
        
        # f is ready to read!
        # Since we are reading conll, we should always get stuff until the next empty line, even if it means blocking read
        while True:
            line=f.readline()
            if not line: #End of file detected --- I guess :D
                if line_buffer:
                    #print("Yielding2",len(list(line for line in line_buffer if line.startswith("1\t"))), file=sys.stderr)
#                    print((dummies+"".join(line_buffer))[:10000],file=sys.stderr)
                    yield dummies+"".join(line_buffer)
                    return
            line_buffer.append(line)
            if not line.strip(): #empty line
                break

        # Now we got the next sentence --- do we have enough to yield?
        if len(line_buffer)>batch_lines:
            #print("Yielding3",len(list(line for line in line_buffer if line.startswith("1\t"))), file=sys.stderr)
            yield dummies+"".join(line_buffer) #got plenty
            line_buffer=[]


  def batch_parse(self,input_files, output_dir=None, output_file=None):
    """
    
    """
    if len(input_files)==1 and not isinstance(input_files[0],str): #Parsing from stdin, batching input
      inp=input_files[0]
      self.parse((io.StringIO(batch) for batch in self.nonblocking_batches(f=inp,batch_lines=1000000)),None,sys.stdout)
      # for batch in self.nonblocking_batches(f=inp):
      #   #batch is a string (piece of the input) let's make it into more pallatable form
      #   pseudofile=io.StringIO(batch)
      #   self.parse([pseudofile],None,sys.stdout)
    else:
      self.parse(input_files, output_dir, output_file) #Normal operation as before

  def parse(self, input_files, output_dir=None, output_file=None):
    """ """

    if isinstance(input_files, types.GeneratorType):
      pass
    else:
      if not isinstance(input_files, (tuple, list)):
        input_files = [input_files]
      if len(input_files) > 1 and output_file is not None:
        raise ValueError('Cannot provide a value for --output_file when parsing multiple files')
      
    with tf.Graph().as_default():
      config_proto = tf.ConfigProto()
      if self.per_process_gpu_memory_fraction == -1:
        config_proto.gpu_options.allow_growth = True
      else:
        config_proto.gpu_options.per_process_gpu_memory_fraction = self.per_process_gpu_memory_fraction
      with tf.Session(config=config_proto) as sess:
        # load the model and prep the parse set

        print("SELF.TRAIN_FILES",self.train_files,file=sys.stderr)
        self.add_file_vocabs(self.train_files)
        self.setup_vocabs()
        trainset = Trainset.from_configurable(self, self.vocabs, nlp_model=self.nlp_model)
        with tf.variable_scope(self.name.title()):
          train_tensors = trainset()
        train_outputs = [train_tensors[train_key] for train_key in trainset.train_keys]

        saver = tf.train.Saver(self.save_vars, max_to_keep=1)
        for var in self.non_save_vars:
          sess.run(var.initializer)
        saver.restore(sess, tf.train.latest_checkpoint(self.save_dir))
        

        
        start_time = time.time()
        for input_file in input_files:

          #print("Parseset vocab")
          self.add_file_vocabs([input_file])

          #print("Beg Parseset.from_configurable")
          parseset = Parseset.from_configurable(self, self.vocabs, parse_files=input_file, nlp_model=self.nlp_model)
          #print("Done Parseset.from_configurable")
          with tf.variable_scope(self.name.title(), reuse=True):
            parse_tensors = parseset(moving_params=self.optimizer)
          parse_outputs = [parse_tensors[parse_key] for parse_key in parseset.parse_keys]

          if not isinstance(input_file,io.StringIO):
            input_dir, input_file = os.path.split(input_file)
            if output_dir is None and output_file is None:
              output_dir = self.save_dir
            if output_dir == input_dir and output_file is None:
              output_path = os.path.join(input_dir, 'parsed-'+input_file)
            elif output_file is None:
              output_path = os.path.join(output_dir, input_file)
            else:
              output_path = output_file
          else:
            assert output_file is not None
            output_path=output_file #The expectation is for this to be an open file

          probs = []
          sents = []
          for feed_dict, tokens in parseset.iterbatches(shuffle=False):
            probs.append(sess.run(parse_outputs, feed_dict=feed_dict))
            sents.append(tokens)
          parseset.write_probs(sents, output_path, probs, parseset._metadata)
          del parseset
      del trainset
      if self.verbose:
        try:
          print(ctext('Parsing {0} file(s) took {1} seconds'.format(len(input_files), time.time()-start_time), 'bright_green'),file=sys.stderr)
        except:
          print(ctext('Parsing took {} seconds'.format(time.time()-start_time), 'bright_green'),file=sys.stderr)
    return

  def parse_generator(self):
    """ This is a (hacky) way to maintain everything loaded. Every time you call __next__() on this generator, it will parse data
        found in self.current_input which should be an open file or StringIO"""

    with tf.Graph().as_default():
      config_proto = tf.ConfigProto()
      if self.per_process_gpu_memory_fraction == -1:
        config_proto.gpu_options.allow_growth = True
      else:
        config_proto.gpu_options.per_process_gpu_memory_fraction = self.per_process_gpu_memory_fraction
      with tf.Session(config=config_proto) as sess:
        # load the model and prep the parse set

        print("SELF.TRAIN_FILES",self.train_files,file=sys.stderr)
        self.add_file_vocabs(self.train_files)
        self.setup_vocabs()
        trainset = Trainset.from_configurable(self, self.vocabs, nlp_model=self.nlp_model)
        with tf.variable_scope(self.name.title()):
          train_tensors = trainset()
        train_outputs = [train_tensors[train_key] for train_key in trainset.train_keys]

        saver = tf.train.Saver(self.save_vars, max_to_keep=1)
        for var in self.non_save_vars:
          sess.run(var.initializer)
        saver.restore(sess, tf.train.latest_checkpoint(self.save_dir))


        while True:
          self.add_file_vocabs([self.current_input])
          parseset = Parseset.from_configurable(self, self.vocabs, parse_files=self.current_input, nlp_model=self.nlp_model)
          with tf.variable_scope(self.name.title(), reuse=True):
            parse_tensors = parseset(moving_params=self.optimizer)
          parse_outputs = [parse_tensors[parse_key] for parse_key in parseset.parse_keys]


          probs = []
          sents = []
          for feed_dict, tokens in parseset.iterbatches(shuffle=False):
            probs.append(sess.run(parse_outputs, feed_dict=feed_dict))
            sents.append(tokens)
          outp=io.StringIO()
          parseset.write_probs(sents, outp, probs, parseset._metadata)
          yield outp.getvalue()
          
          del parseset
      del trainset
      if self.verbose:
        try:
          print(ctext('Parsing {0} file(s) took {1} seconds'.format(len(input_files), time.time()-start_time), 'bright_green'),file=sys.stderr)
        except:
          print(ctext('Parsing took {} seconds'.format(time.time()-start_time), 'bright_green'),file=sys.stderr)
    return


  
  #=============================================================
  @property
  def vocabs(self):
    return self._vocabs
  @property
  def datasets(self):
    return self._datasets
  @property
  def optimizer(self):
    return self._optimizer
  @property
  def save_vars(self):
    return [x for x in tf.global_variables() if 'Pretrained/Embeddings:0' != x.name]
  @property
  def non_save_vars(self):
    return [x for x in tf.global_variables() if 'Pretrained/Embeddings:0' == x.name]
  @property
  def global_step(self):
    return self._global_step
  @property
  def global_epoch(self):
    return self._global_epoch

#***************************************************************
if __name__ == '__main__':
  """ """
  
  from nparser import Network
  configurable = Configurable()
  network = Network.from_configurable(configurable)
  network.train()
