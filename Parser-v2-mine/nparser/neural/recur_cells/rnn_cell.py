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

#***************************************************************
class RNNCell(BaseCell):
  """ """
  
  #=============================================================
  def __call__(self, inputs, state, scope=None):
    """ """
    
    with tf.variable_scope(scope or type(self).__name__):
      inputs_list = [inputs, state]
      hidden_act = linear(inputs_list,
                          self.output_size,
                          add_bias=True,
                          moving_params=self.moving_params)
      hidden = self.recur_func(hidden_act)
    return hidden, hidden
  
  #=============================================================
  @property
  def state_size(self):
    return self.output_size
  
