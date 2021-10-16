# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import json, os, math
from collections import defaultdict

"""
Utilities for working with function program representations of questions.

Some of the metadata about what question node types are available etc are stored
in a JSON metadata file.
"""


# Handlers for answering questions. Each handler receives the scene structure
# that was output from Blender, the node, and a list of values that were output
# from each of the node's inputs; the handler should return the computed output
# value from this node.


def scene_handler(scene_struct, inputs, side_inputs):
  # Just return all objects in the scene
  return list(range(len(scene_struct['objects'])))


def make_filter_handler(attribute):
  def filter_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 1
    assert len(side_inputs) == 1
    value = side_inputs[0]
    output = []
    for idx in inputs[0]:
      atr = scene_struct['objects'][idx][attribute]
      if value == atr or value in atr:
        output.append(idx)
    return output
  return filter_handler


def unique_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 1
  if len(inputs[0]) != 1:
    return '__INVALID__'
  return inputs[0][0]


def vg_relate_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 1
  assert len(side_inputs) == 1
  output = set()
  for rel in scene_struct['relationships']:
    if rel['predicate'] == side_inputs[0] and rel['subject_idx'] == inputs[0]:
      output.add(rel['object_idx'])
  return sorted(list(output))



def relate_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 1
  assert len(side_inputs) == 1
  relation = side_inputs[0]
  return scene_struct['relationships'][relation][inputs[0]]
    

def union_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 2
  assert len(side_inputs) == 0
  return sorted(list(set(inputs[0]) | set(inputs[1])))


def intersect_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 2
  assert len(side_inputs) == 0
  return sorted(list(set(inputs[0]) & set(inputs[1])))


def count_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 1
  if len(inputs[0]) == 1:
    
    return ("Yes, it is ")
  elif len(inputs[0]) == 0:
    return ("No (we cannot find the thing meet the requirement)")
  else:
    return (len(inputs[0]))



def make_same_attr_handler(attribute):
  def same_attr_handler(scene_struct, inputs, side_inputs):
    cache_key = '_same_%s' % attribute
    if cache_key not in scene_struct:
      cache = {}
      for i, obj1 in enumerate(scene_struct['objects']):
        same = []
        for j, obj2 in enumerate(scene_struct['objects']):
          if i != j and obj1[attribute] == obj2[attribute]:
            same.append(j)
        cache[i] = same
      scene_struct[cache_key] = cache

    cache = scene_struct[cache_key]
    assert len(inputs) == 1
    assert len(side_inputs) == 0
    return cache[inputs[0]]
  return same_attr_handler


def make_query_handler(attribute):
  def query_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 1
    assert len(side_inputs) == 0
    idx = inputs[0]
    obj = scene_struct['objects'][idx]
    assert attribute in obj
    val = obj[attribute]
    if type(val) == list and len(val) != 1:
      return '__INVALID__'
    elif type(val) == list and len(val) == 1:
      return val[0]
    else:
      return val
  return query_handler


def exist_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 1
  assert len(side_inputs) == 0
  return len(inputs[0]) > 0


def equal_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 2
  assert len(side_inputs) == 0
  return inputs[0] == inputs[1]


def less_than_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 2
  assert len(side_inputs) == 0
  return inputs[0] < inputs[1]


def greater_than_handler(scene_struct, inputs, side_inputs):
  assert len(inputs) == 2
  assert len(side_inputs) == 0
  return inputs[0] > inputs[1]

def generate_text_handler(scene_struct, inputs, side_inputs):
  if inputs[0] == False:
    return ("No (we cannot find the thing meet the requirement)")
  elif inputs[0] == True:
    return (str(str("Yes, It is ")+str(inputs[1])))

def text_handler_oh1(scene_struct, inputs, side_inputs):
  if inputs[0] == "No (we cannot find the thing meet the requirement)":
    return ("No (we cannot find the thing meet the requirement)")
  elif inputs[0] == "Yes, it is ":
    return (str(str("It is only one, which is ")+str(inputs[-1])))
  else:
    return(str(str("The number is ")+str(inputs[0])))

def text_handler_oh2(scene_struct, inputs, side_inputs):
  return(inputs[0][0])

def text_handler_oh3(scene_struct, inputs, side_inputs):
  if inputs[0] == False:
    return ("We cannot find the thing meet the requirement")
  elif inputs[0] == True:
    return (str(str("It is ")+str(inputs[1])))

def text_handler_th1(scene_struct, inputs, side_inputs):
  if inputs[0] == False:
    return ("No (we cannot find the thing meet the requirement)")
  elif inputs[0] == True:
    return (str(str("Yes")))

def text_handler_oh4(scene_struct, inputs, side_inputs):
  if inputs[0] == child:
    return ("No (we cannot find the thing meet the requirement)")
  elif inputs[0] == True:
    return (str(str("Yes")))

def make_filter_handler1(scene_struct, inputs, side_inputs):
  if inputs[0][0] == 'child':
    temp_atr = scene_struct["objects"][int(inputs[0][1])]['size']
    return temp_atr
  if inputs[0][0] == 'parent':
    return (str("No title"))
def filter_shape_count(scene_struct, inputs, side_inputs):
  if len(inputs[0]) == 1:
    return ("There is only one")
  elif len(inputs[0]) == 0:
    return ("No (we cannot find the thing meet the requirement)")
  else:
    return (len(inputs[0]))

def all_output(a):
  for x in a:
    if a.index(x) == 0:
      temp = x.rstrip()
    else:
      temp = temp + ',' + x.rstrip()
  return temp
    

def xxx(p1,p2,p3):
  def XXX(scene_struct, inputs, side_inputs):
    child = ['text', 'table', 'figure','list']
    # parent = ['title', 'table_caption', 'figure_caption', 'list']
    B=[] 
    T=""
    output=[]
    output_top = []
    output_bottom = []

    output_f = []
    output_top_f = []
    output_bottom_f = []

    hint=""
    for idx in inputs[0]:
      T = scene_struct['objects'][idx]["shape"]
      if T==p1:
        B=scene_struct['objects'][idx]["bbox"]
        
        if p2=="left" and (int(B[0])<200 and int(B[2])<300):
          output.append(scene_struct['objects'][idx]["size"])
          output_f += scene_struct['objects'][idx]["family"]
          if int(B[3] < 400):
            output_top.append(scene_struct['objects'][idx]["size"])
            output_top_f += scene_struct['objects'][idx]["family"]
          else:
            output_bottom.append(scene_struct['objects'][idx]["size"])
            output_bottom_f += scene_struct['objects'][idx]["family"]
        elif p2=="right" and (int(B[0])>300 and int(B[2])<300):
          output.append(scene_struct['objects'][idx]["size"])
          output_f += scene_struct['objects'][idx]["family"]
          if int(B[3] < 400):
            output_top.append(scene_struct['objects'][idx]["size"])
            output_top_f += scene_struct['objects'][idx]["family"]
          else:
            output_bottom.append(scene_struct['objects'][idx]["size"])
            output_bottom_f += scene_struct['objects'][idx]["family"]
        if int(B[2])>300:
          hint="This page is Centered layout"
      else:
        hint= "There is no " +p1+" in the "+p3+" of page"

    #获取关系中的size
    new = set()
    new_t = set()
    new_b = set()
    for i in output_f:
      new.add(scene_struct['objects'][int(i[1])]["size"])
    for i in output_top_f:
      new_t.add(scene_struct['objects'][int(i[1])]["size"])
    for i in output_bottom_f:
      new_b.add(scene_struct['objects'][int(i[1])]["size"])

    new = list(new)
    new_t = list(new_t)
    new_b = list(new_b)


    if p1 in child:
      if (p3 == 'left' or p3 == 'right'):
        if new ==[]:
          return 'It is unclear'
        else:
          return all_output(new)
      if p3 == 'top left' or p3 == 'top right':
        if new_t == []:
          return 'It is unclear'
        else:
          return all_output(new_t)
      if p3 == 'bottom left' or p3 == 'bottom right':
        if new_b == []:
          return 'It is unclear'
        else:
          return all_output(new_b)

    else:
      if (p3 == 'left' or p3 == 'right'):
        if output ==[]:
          return hint
        else:
          return all_output(output)
      if p3 == 'top left' or p3 == 'top right':
        if output_top == []:
          return "There is no " +p1+" in the "+p3+" of page"
        else:
          return all_output(output_top)
      if p3 == 'bottom left' or p3 == 'bottom right':
        if output_bottom == []:
          return "There is no " +p1+" in the "+p3+" of page"
        else:
          return all_output(output_bottom)


    # if (p3 == 'left' or p3 == 'right'):
    #   if output ==[]:
    #     return hint
    #   else:
    #     return all_output(output)
    # if p3 == 'top left' or p3 == 'top right':
    #   if output_top == []:
    #     return "There is no " +p1+" in the "+p3+" of page"
    #   else:
    #     return all_output(output_top)
    # if p3 == 'bottom left' or p3 == 'bottom right':
    #   if output_bottom == []:
    #     return "There is no " +p1+" in the "+p3+" of page"
    #   else:
    #     return all_output(output_bottom)
    
  return XXX
# def filter_shape_count(scene_struct, _output, side_inputs):
#   temp_count = 0
#   for i in _output:
#     if scene_struct["objects"][int(i)]['shape'] == 'title':
#       temp_count += 1
#   if temp_count == 1:
#     return ("There is only one")
#   elif temp_count == 0:
#     return ("No (we cannot find the thing meet the requirement)")
#   else:
#     return (temp_count)
# Register all of the answering handlers here.
# TODO maybe this would be cleaner with a function decorator that takes
# care of registration? Not sure. Also what if we want to reuse the same engine
# for different sets of node types?
execute_handlers = {
  'make_position_title_l': xxx('title','left','left'),
  'make_position_title_l_top': xxx('title','left','top left'),
  'make_position_title_l_bottom': xxx('title','left','bottom left'),

  'make_position_title_r': xxx('title','right','right'),
  'make_position_title_r_top': xxx('title','right','top right'),
  'make_position_title_r_bottom': xxx('title','right','bottom right'),

  'make_position_text_l': xxx('text','left','left'),
  'make_position_text_l_top': xxx('text','left','top left'),
  'make_position_text_l_bottom': xxx('text','left','bottom left'),

  'make_position_text_r': xxx('text','right','right'),
  'make_position_text_r_top': xxx('text','right','top right'),
  'make_position_text_r_bottom': xxx('text','right','bottom right'),

  'make_position_table_caption_l': xxx('table_caption','left','right'),
  'make_position_table_caption_l_top': xxx('table_caption','left','top right'),
  'make_position_table_caption_l_bottom': xxx('table_caption','left','bottom right'),

  'make_position_table_caption_r': xxx('table_caption','right','right'),
  'make_position_table_caption_r_top': xxx('table_caption','right','top right'),
  'make_position_table_caption_r_bottom': xxx('table_caption','right','bottom right'),

  'make_position_table_l': xxx('table','left','left'),
  'make_position_table_l_top': xxx('table','left','top left'),
  'make_position_table_l_bottom': xxx('table','left','bottom left'),

  'make_position_table_r': xxx('table','right','right'),
  'make_position_table_r_top': xxx('table','right','top right'),
  'make_position_table_r_bottom': xxx('table','right','bottom right'),

  'make_position_list_l': xxx('list','left','left'),
  'make_position_list_l_top': xxx('list','left','top left'),
  'make_position_list_l_bottom': xxx('list','left','bottom left'),

  'make_position_list_r': xxx('list','right','right'),
  'make_position_list_r_top': xxx('list','right','top right'), 
  'make_position_list_r_bottom': xxx('list','right','bottom right'),

  'make_position_figure_l': xxx('figure','left','left'),
  'make_position_figure_l_top': xxx('figure','left','top left'),
  'make_position_figure_l_bottom': xxx('figure','left','bottom left'),

  'make_position_figure_r': xxx('figure','right','right'),
  'make_position_figure_r_top': xxx('figure','right','top right'),
  'make_position_figure_r_bottom': xxx('figure','right','bottom right'),

  'make_position_figure_caption_l': xxx('figure_caption','left','left'),
  'make_position_figure_caption_l_top': xxx('figure_caption','left','top left'),
  'make_position_figure_caption_l_bottom': xxx('figure_caption','left','bottom left'),

  'make_position_figure_caption_r': xxx('figure_caption','right','right'),
  'make_position_figure_caption_r_top': xxx('figure_caption','right','top right'),
  'make_position_figure_caption_r_bottom': xxx('figure_caption','right','bottom right'),

  'filter_shape_count': filter_shape_count,
  'make_filter_handler1': make_filter_handler1,
  'text_handler_oh3': text_handler_oh4,
  'text_handler_oh3': text_handler_oh3,
  'text_handler_th1': text_handler_th1,
  'text_handler_oh2': text_handler_oh2,
  'query_family':make_query_handler('family'),
  'text_handler_oh1': text_handler_oh1,
  'generate_text': generate_text_handler,
  'scene': scene_handler,
  'filter_color': make_filter_handler('color'),
  'filter_shape': make_filter_handler('shape'),
  'filter_material': make_filter_handler('material'),
  'filter_size': make_filter_handler('size'),
  'filter_text': make_filter_handler('text'),
  'filter_objectcategory': make_filter_handler('objectcategory'),
  'unique': unique_handler,
  'relate': relate_handler,
  'union': union_handler,
  'intersect': intersect_handler,
  'count': count_handler,
  'query_color': make_query_handler('color'),
  'query_shape': make_query_handler('shape'),
  'query_material': make_query_handler('material'),
  'query_size': make_query_handler('size'),
  'query_text': make_query_handler('text'),
  'exist': exist_handler,
  'equal_color': equal_handler,
  'equal_shape': equal_handler,
  'equal_integer': equal_handler,
  'equal_material': equal_handler,
  'equal_size': equal_handler,
  'equal_object': equal_handler,
  'less_than': less_than_handler,
  'greater_than': greater_than_handler,
  'same_color': make_same_attr_handler('color'),
  'same_shape': make_same_attr_handler('shape'),
  'same_size': make_same_attr_handler('size'),
  'same_material': make_same_attr_handler('material'),
}


def answer_question(question, metadata, scene_struct, all_outputs=False,
                    cache_outputs=True):
  """
  Use structured scene information to answer a structured question. Most of the
  heavy lifting is done by the execute handlers defined above.

  We cache node outputs in the node itself; this gives a nontrivial speedup
  when we want to answer many questions that share nodes on the same scene
  (such as during question-generation DFS). This will NOT work if the same
  nodes are executed on different scenes.
  """
  all_input_types, all_output_types = [], []
  node_outputs = []
  for node in question['nodes']:
    if cache_outputs and '_output' in node:
      node_output = node['_output']
    else:
      node_type = node['type']
      msg = 'Could not find handler for "%s"' % node_type
      assert node_type in execute_handlers, msg
      handler = execute_handlers[node_type]
      node_inputs = [node_outputs[idx] for idx in node['inputs']]
      side_inputs = node.get('side_inputs', [])
      node_output = handler(scene_struct, node_inputs, side_inputs)
      if cache_outputs:
        node['_output'] = node_output
    node_outputs.append(node_output)
    if node_output == '__INVALID__':
      break

  if all_outputs:
    return node_outputs
  else:
    return node_outputs[-1]


def insert_scene_node(nodes, idx):
  # First make a shallow-ish copy of the input
  new_nodes = []
  for node in nodes:
    new_node = {
      'type': node['type'],
      'inputs': node['inputs'],
    }
    if 'side_inputs' in node:
      new_node['side_inputs'] = node['side_inputs']
    new_nodes.append(new_node)

  # Replace the specified index with a scene node
  new_nodes[idx] = {'type': 'scene', 'inputs': []}

  # Search backwards from the last node to see which nodes are actually used
  output_used = [False] * len(new_nodes)
  idxs_to_check = [len(new_nodes) - 1]
  while idxs_to_check:
    cur_idx = idxs_to_check.pop()
    output_used[cur_idx] = True
    idxs_to_check.extend(new_nodes[cur_idx]['inputs'])

  # Iterate through nodes, keeping only those whose output is used;
  # at the same time build up a mapping from old idxs to new idxs
  old_idx_to_new_idx = {}
  new_nodes_trimmed = []
  for old_idx, node in enumerate(new_nodes):
    if output_used[old_idx]:
      new_idx = len(new_nodes_trimmed)
      new_nodes_trimmed.append(node)
      old_idx_to_new_idx[old_idx] = new_idx

  # Finally go through the list of trimmed nodes and change the inputs
  for node in new_nodes_trimmed:
    new_inputs = []
    for old_idx in node['inputs']:
      new_inputs.append(old_idx_to_new_idx[old_idx])
    node['inputs'] = new_inputs

  return new_nodes_trimmed


def is_degenerate(question, metadata, scene_struct, answer=None, verbose=False):
  """
  A question is degenerate if replacing any of its relate nodes with a scene
  node results in a question with the same answer.
  """
  if answer is None:
    answer = answer_question(question, metadata, scene_struct)

  for idx, node in enumerate(question['nodes']):
    if node['type'] == 'relate':
      new_question = {
        'nodes': insert_scene_node(question['nodes'], idx)
      }
      new_answer = answer_question(new_question, metadata, scene_struct)
      if verbose:
        print('here is truncated question:')
        for i, n in enumerate(new_question['nodes']):
          name = n['type']
          if 'side_inputs' in n:
            name = '%s[%s]' % (name, n['side_inputs'][0])
          print(i, name, n['_output'])
        print('new answer is: ', new_answer)

      if new_answer == answer:
        return True

  return False

