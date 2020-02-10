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





import tensorflow as tf

from nparser.neural.recur_cells.base_cell import BaseCell
from nparser.neural.linalg import linear
from nparser.neural.functions import gate

#***************************************************************
class CifLSTMCell(BaseCell):
  """ """
  
  #=============================================================
  def __call__(self, inputs, state, scope=None):
    """ """
    
    with tf.variable_scope(scope or type(self).__name__):
      cell_tm1, hidden_tm1 = tf.split(state, 2, axis=1)
      input_list = [inputs, hidden_tm1]
      lin = linear(input_list,
                   self.output_size,
                   add_bias=True,
                   n_splits=3,
                   moving_params=self.moving_params)
      cell_act, update_act, output_act = lin
      
      cell_tilde_t = cell_act
      update_gate = gate(update_act-self.forget_bias)
      output_gate = gate(output_act)
      cell_t = update_gate * cell_tilde_t + (1-update_gate) * cell_tm1
      hidden_tilde_t = self.recur_func(cell_t)
      hidden_t = hidden_tilde_t * output_gate
      
      return hidden_t, tf.concat([cell_t, hidden_t], 1)
  
  #=============================================================
  @property
  def state_size(self):
    return self.output_size * 2
  
