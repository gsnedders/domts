""" domts.inbuilts: define which TSML elements are simple in-built functions
    that can be defined in a data-driven way. The more involved in-built
    functionality is done directly in the interpreter.
"""

__all__= [
  'CONSTANTS', 'CONDITIONS', 'ASSERTS', 'EXCEPTIONASSERTS', 'UNARYOPS',
  'BINARYOPS', 'CONDITIONOPS', 'IGNORE', 'ACTUALS', 'EXPECTEDS'
]

import operator
from UserList import UserList
try: True
except NameError: globals()['True'],globals()['False']= not None, not not None


# Simple comparators for CONDITIONS map
#
def scmp(a, e, cs= True):
  """ Compare a string or list of strings, possibly case-sensitively.
  """
  if not cs:
    if hasattr(a, 'lower'):
      a= a.lower()
    if hasattr(e, 'lower'):
      e= e.lower()
  return a==e

def inst(a, e, cs= True):
  """ Try to check an object implements a given interface. This is unreliable
      in Python as there are no interfaces. For Nodes we just check the
      nodeType.
  """
  return getattr(a, 'nodeType', None)==e


# Constants that TSML expressions may want to use.
#
CONSTANTS= {
  'null': None, 'auto': None,
  'true': True, 'false': False,
  'Element': 1, 'Attr': 2, 'Text': 3, 'CDATASection': 4, 'EntityReference': 5,
  'Entity': 6, 'ProcessingInstruction': 7, 'Comment': 8, 'Document': 9,
  'DocumentType': 10, 'DocumentFragment': 11, 'Notation': 12
}

# Conditions. Used by the nested condition element of an <if>/<while>, and,
# when prefixed 'assert', as assertions. (TSML doesn't actually quite work
# like this, but near enough.
#
CONDITIONS= {
  'equals': scmp,
  'notEquals': lambda a, e, cs: not scmp(a, e, cs),
  'null': lambda a, e, cs: a is None,
  'isNull': lambda a, e, cs: a is None,
  'notNull': lambda a, e, cs: a is not None,
  'true': lambda a, e, cs: a,
  'false': lambda a, e, cs: not a,
  'isTrue': lambda a, e, cs: e,
  'isFalse': lambda a, e, cs: not e,
  'size': lambda a, e, cs: len(a)==e,
  'same': lambda a, e, cs: a is e,
  'uRIEquals': scmp,
  'instanceOf': inst,
  'contentType': scmp,
  'implementationAttribute': scmp
}

ACTUALS= ['actual', 'obj', 'collection']
EXPECTEDS= ['expected', 'size', 'file', 'value', 'type']

ASSERTS= []
for condition, comparer in CONDITIONS.items():
  ASSERTS.append('assert'+condition[0].upper()+condition[1:])

EXCEPTIONASSERTS= [
  'assertDOMException','assertXPathException','assertImplementationException'
]

UNARYOPS= {
  'increment': operator.add,
  'decrement': operator.sub,
}

BINARYOPS= {
  'plus': operator.add,
  'subtract': operator.sub,
  'mult': operator.mul,
  'divide': operator.div,
}

CONDITIONOPS= {
  'and': lambda a, b: a and b,
  'or': lambda a, b: a or b,
  'xor': lambda a, b: operator.truth(a)!=operator.truth(b)
}

# Elements to ignore when encountered in statement context
#
IGNORE= ['comment', 'metadata', 'else']


class OrderedList(UserList):
  """ List that can be recursively lowercased for comparison purposes.
  """
  def __init__(self, data= []):
    self.data= data[:]
  def lower(self):
    lower= []
    for datum in self.data:
      lower.append(datum.lower())
    return lower

class UnorderedList(OrderedList):
  """ List used for non-ordered Collection objects. When being compared, the
      order of members is irrelevant. This should ideally be a Python Set, but
      we don't need the can-only-contain-one-identical-item restriction in any
      of the current tests, and don't want to require Python 2.3.
  """
  def __cmp__(self, other):
    if not isinstance(other, OrderedList):
      return 1
    if len(other)!=len(self):
      return 1
    for datum in self.data:
      if not datum in other:
        return 1
    return 0
  def __eq__(self, other):
    return self.__cmp__(other)==0
  def __ne__(self, other):
    return self.__cmp__(other)!=0


OBJECTS={
  'Collection': UnorderedList,
  'List':       OrderedList
}

class TestCreatedObject:
  """ Object created by a TS test, which must then fill in the members itself.
      Method members are added by nasty magic.
  """
  def __getattr__(self, attr):
    if self.__dict__.has_key('_meth_'+attr):
      return self.__dict__['_meth_'+attr]
    elif self.__dict__.has_key('_get_'+attr):
      return self.__dict__['_get_'+attr]()
    else:
      raise AttributeError('No attribute %s (or getter) in TSML object' % attr)
  def __setattr__(self, attr, value):
    if self.__dict__.has_key('_set_'+attr):
      self.__dict__['_set_'+attr](value)
    else:
      self.__dict__[attr]= value

  def setGetter(self, attr, method):
    self.__dict__['_get_'+attr]= method
  def setSetter(self, attr, method):
    self.__dict__['_set_'+attr]= method
  def setMethod(self, attr, method):
    self.__dict__['_meth_'+attr]= method
