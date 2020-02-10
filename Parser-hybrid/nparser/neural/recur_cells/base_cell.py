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

from nparser.configurable import Configurable

#***************************************************************
class BaseCell(Configurable):
  """ """
  
  #=============================================================
  def __init__(self, output_size, *args, **kwargs):
    """ """
    
    self._output_size = output_size
    input_size = kwargs.pop('input_size', self._output_size)
    self.moving_params = kwargs.pop('moving_params', None)
    super(BaseCell, self).__init__(*args, **kwargs)
    self._input_size = input_size if input_size is not None else self.output_size
  
  #=============================================================
  def __call__(self, inputs, state, scope=None):
    """ """
    
    raise NotImplementedError()
  
  #=============================================================
  def zero_state(self, batch_size, dtype):
    """ """
    
    zero_state = tf.get_variable('Zero_state',
                                 shape=self.state_size,
                                 dtype=dtype,
                                 initializer=tf.zeros_initializer())
    state = tf.reshape(tf.tile(zero_state, tf.stack([batch_size])), tf.stack([batch_size, self.state_size]))
    state.set_shape([None, self.state_size])
    return state
  
  #=============================================================
  @property
  def input_size(self):
    return self._input_size
  @property
  def output_size(self):
    return self._output_size
  @property
  def state_size(self):
    raise NotImplementedError()
