# coding=utf-8
# Copyright 2018 The TensorFlow Datasets Authors.
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

"""TensorFlow utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import numpy as np
import tensorflow as tf


# Struct containing a graph for the TFGraphRunner
GraphRun = collections.namedtuple(
    'GraphRun', 'graph, session, placeholder, output')

# Struct containing the run args, kwargs
RunArgs = collections.namedtuple('RunArgs', 'fct, input')


class TFGraphRunner(object):
  """Run in session mode or Eager mode.

  This is a compatibility util between graph and eager TensorFlow.

  The graph runner allow to run function defining small TensorFlow graphs:
   * In eager mode: The function is simply run eagerly and the result is
     returned
   * In graph mode: The first time, the function is compiled in a new graph,
     then, every time the same function will be called, the cached graph and
     session will be run.

  Ideally, one graph runner should only be used with a single function to avoid
  having too many opened session in session mode.
  Limitations:
   * Currently the graph runner only support function with single input
     and output. Support for more complex function could be added and should be
     relativelly straighforward.
   * A different graph is created for each input shape, so isn't really addapted
     for dynamic batch size.

  Usage:
    graph_runner = TFGraphRunner()
    output = graph_runner.run(tf.sigmoid, np.ones(shape=(5,)))

  """

  def __init__(self):
    """Constructor."""
    # Cache containing all compiled graph and opened session. Only used in
    # non-eager mode.
    self._graph_run_cache = {}

  def run(self, fct, input_):
    """Execute the given TensorFlow function."""
    # TF 2.0
    if tf.executing_eagerly():
      return fct(input_).numpy()
    # TF 1.0
    else:
      # Should compile the function if this is the first time encountered
      if not isinstance(input_, np.ndarray):
        input_ = np.array(input_)
      run_args = RunArgs(fct=fct, input=input_)
      signature = self._build_signature(run_args)
      if signature not in self._graph_run_cache:
        graph_run = self._build_graph_run(run_args)
        self._graph_run_cache[signature] = graph_run
      else:
        graph_run = self._graph_run_cache[signature]

      # Then execute the cached graph
      return graph_run.session.run(
          graph_run.output,
          feed_dict={graph_run.placeholder: input_},
      )

  def _build_graph_run(self, run_args):
    """Create a new graph for the given args."""
    # Could try to use tfe.py_func(fct) but this would require knowing
    # information about the signature of the function.

    # Create a new graph:
    with tf.Graph().as_default() as g:
      # Create placeholder
      input_ = run_args.input
      placeholder = tf.placeholder(dtype=input_.dtype, shape=input_.shape)
      output = run_args.fct(placeholder)
      return GraphRun(
          session=tf.Session(),
          graph=g,
          placeholder=placeholder,
          output=output,
      )

  def _build_signature(self, run_args):
    """Create a unique signature for each fct/inputs."""
    return (id(run_args.fct), run_args.input.dtype, run_args.input.shape)

  def __del__(self):
    # Close all sessions
    for graph_run in self._graph_run_cache.values():
      graph_run.session.close()


def is_dytpe(value):
  """Return True is the given value is a TensorFlow dtype."""
  try:
    tf.as_dtype(value)
  except TypeError:
    return False
  return True


def assert_shape_match(shape1, shape2):
  """Ensure the shape1 match the pattern given by shape2.

  Ex:
    assert_shape_match((64, 64, 3), (None, None, 3))

  Args:
    shape1 (tuple): Static shape
    shape2 (tuple): Dyncamic shape (can contains None)
  """
  if len(shape1) != len(shape2):
    raise ValueError('Shapes should have same length: {} - {}'.format(
        len(shape1), len(shape2)))
  if not all(
      s1 == s2  # All shape should match
      for s1, s2 in zip(shape1, shape2)
      if s2 is not None):
    raise ValueError('Shape {} do not match {}'.format(shape1, shape2))
