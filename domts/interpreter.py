""" domts.interpreter: main TSML test runner
"""

__all__= ['Tester']

import os, sys, urllib, tempfile, random
from inbuilts import *
from interfaces import *
from interrupter import *

try: True
except NameError: globals()['True'],globals()['False']= not None, not not None
NonErrors= (KeyboardInterrupt, SystemExit, SystemError, MemoryError)
sstr= lambda x: unicode(x).encode('us-ascii', 'replace')

class TestException(Exception):
  """ An exception occurred whilst running a test. This will cause the test to
      fail unless it is caught in a parent assertException element.
  """
  def __init__(self, description, exception):
    Exception.__init__(self, description)
    self.exception= exception
  def __str__(self):
    return '%s: %s, %s' % (Exception.__str__(self),
      self.exception.__class__.__name__, str(self.exception)
    )

class ReturnValue(Exception):
  """ A test-created method used a <return> element. Must be caught by a
      TSMethod object that caused the method to be called.
  """
  def __init__(self, value):
    Exception.__init__(self, 'A <return> element was used.')
    self.value= value


class Tester:
  def __init__(self, implementation, filesPath):
    self.implementation= implementation
    self.filesPath= filesPath
    self.scope= CONSTANTS.copy()
    self.globalScope= None

  def runTest(self, testDoc):
    self.tempFiles= []
    testRoot= testDoc.documentElement
    testName= testRoot.getAttribute('name')
    try:
      try:
        self.process(testRoot.childNodes)
      except NotImplementedError, e:
        return (testName, False, True, e)
      except (AssertionError, TestException), e:
        return (testName, False, False, e)
      except ReturnValue, e:
        if e is not None:
          raise
      return (testName, True, False, None)
    finally:
      for path in self.tempFiles:
        try:
          os.remove(path)
        except OSError:
          pass


  def process(self, children):
    """ Execute a list of TSML command nodes.
    """
    for child in children:
      if child.nodeType!=child.ELEMENT_NODE:
        continue
      t= child.tagName

      # Special case - hasFeature can be a method call, or an implementation
      # check if no object is passed
      #
      if t=='hasFeature' and not child.hasAttribute('obj'):
        feature= self.ueval(child.getAttribute('feature'))
        version= self.ueval(child.getAttribute('version') or 'null')
        try:
          hasFeature= self.implementation.implementation.hasFeature(
            feature,version
          )
        except NonErrors:
          raise
        except Exception:
          hasFeature= False
        if not hasFeature:
          raise NotImplementedError('Feature %s %s' % (feature, version))

      # Deal with other elements
      #
      elif t in IGNORE:
        pass
      elif METHODS.has_key(t):
        self.callMethod(child)
      elif t=='implementation' and not child.hasAttribute('obj'):
        # special case, implementation can be got without using obj property
        varName= child.getAttribute('var')
        self.scope[varName]= self.implementation.implementation
      elif t in PROPERTIES:
        if child.hasAttribute('value'):
          self.setProperty(child)
        else:
          self.getProperty(child)
      elif t in ASSERTS:
        self.makeAssertion(child)
      elif t in EXCEPTIONASSERTS:
        self.exceptionAssertion(child)
      elif UNARYOPS.has_key(t):
        varName= child.getAttribute('var')
        value= self.ueval(child.getAttribute('value'))
        self.scope[varName]= UNARYOPS[t](self.scope[varName], value)
      elif BINARYOPS.has_key(t):
        op1= self.ueval(child.getAttribute('op1'))
        op2= self.ueval(child.getAttribute('op2'))
        self.scope[child.getAttribute('var')]= BINARYOPS[t](op1, op2)
      elif t=='assign':
        varName= child.getAttribute('var')
        self.scope[varName]= self.ueval(child.getAttribute('value'))
      elif t=='append':
        varName= child.getAttribute('collection')
        if child.hasAttribute('item'):
          member= self.ueval(child.getAttribute('item'))
        else:
          member= self.scope[child.getAttribute('obj')]
        self.scope[varName].append(member)
      elif t=='substring':
        ix0= self.ueval(child.getAttribute('beginIndex'))
        ix1= self.ueval(child.getAttribute('endIndex'))
        substr= self.scope[child.getAttribute('obj')][ix0:ix1]
        self.scope[child.getAttribute('var')]= substr
      elif t=='for-each':
        self.forLoop(child)
      elif t=='while':
        self.whileLoop(child)
      elif t=='if':
        self.ifCondition(child)
      elif t=='try':
        self.tryBlock(child)
      elif t=='fail':
        name= child.getAttribute('id')
        raise AssertionError('Assertion %s failed, no exception' % name)
      elif t=='return':
        if child.hasAttribute('value'):
          raise ReturnValue(self.ueval(child.getAttribute('value')))
        raise ReturnValue(None)
      elif t=='var':
        (varName, initialValue)= self.readVar(child)
        self.scope[varName]= initialValue
      elif t=='implementationAttribute':
        attr= child.getAttribute('name')
        value= self.ueval(child.getAttribute('value'))
        self.implementation.setImplementationAttribute(attr, value)
      elif t in ('load', 'getResourceURI'):
        varName= child.getAttribute('var')
        ext= self.implementation.extension
        if child.getAttribute('href')=='TESTPDF':
          ext= '.pdf'
        filePath= os.path.join(self.filesPath, child.getAttribute('href').lower()+ext)
        if t=='getResourceURI':
          self.scope[varName]= 'file:'+urllib.pathname2url(filePath)
        else:
          try:
            self.scope[varName]= self.implementation.parseFile(filePath)
          except NonErrors:
            raise
          except Exception, e:
            raise TestException('Document load failed', e)
      elif t=='createTempURI':
        scheme= child.getAttribute('scheme')
        if scheme=='file':
          filePath= tempfile.mktemp()
          self.tempFiles.append(filePath)
          varName= child.getAttribute('var')
          self.scope[varName]= 'file:'+urllib.pathname2url(filePath)
        elif scheme=='http':
          self.scope[child.getAttribute('var')]= (
            'http://localhost:8080/domts/temp/%d.xml'%int(random.random()*10000)
          )
        else:
          raise NotImplementedError('Unknown scheme '+scheme)
      elif t=='createXPathEvaluator':
        self.scope[child.getAttribute('var')]= (
          self.ueval(child.getAttribute('document'))
        )
      elif t=='debug':
        print self.ueval(child.getAttribute('out'))
      elif t=='DOMImplementationRegistry.newInstance':
        raise NotImplementedError('DOMImplementationRegistry is not bound in Python')
      else:
        raise NotImplementedError('Unknown TSML element %s' % t)


  def callMethod(self, testNode):
    methodName= testNode.tagName
    obj= self.ueval(testNode.getAttribute('obj'))
    if not hasattr(obj, testNode.tagName):
      raise TestException('Missing method %s on %s' % (
        methodName, str(obj)), AttributeError()
      )
    method= getattr(obj, methodName)
    arguments= []
    for par in METHODS[testNode.tagName]:
      if not testNode.hasAttribute(par):
        # special case, acceptNode has different arg names depending on its
        # object.
        if par=='nodeArg':
          par= 'n'
      if not testNode.hasAttribute(par):
        if par=='version':
          # special case, hasFeature can omit version arg
          arguments.append(None)
        elif methodName=='evaluate':
          # special case, there are two 'evaluate' methods on
          # different objects. One omits a couple of arguments.
          pass
        else:
          raise ValueError('TSML argument attribute %s missing' % par)
      else:
        arguments.append(self.ueval(testNode.getAttribute(par)))
    interrupter= Interrupter()
    try:
      interrupter.start()
      try:
        value= apply(method, arguments)
      finally:
        interrupter.finish()
    except NonErrors:
      raise
    except (TestException, AssertionError, ReturnValue):
      raise
    except Exception, e:
      raise TestException('Calling %s on %s' % (methodName, str(obj)), e)
    if testNode.hasAttribute('var'):
      self.scope[testNode.getAttribute('var')]= value


  def getProperty(self, testNode):
    obj= self.ueval(testNode.getAttribute('obj'))
    propName= testNode.tagName

    # Python binds DOMString to native strings (either type). These have no
    # 'length' property as required by some tests, so simulate this.
    #
    if propName=='length' and type(obj) in (type(''), type(u'')):
      value= len(obj)
    else:

      # Try to read property
      #
      interrupter= Interrupter()
      try:
        interrupter.start()
        try:
          value= getattr(obj, propName)
        finally:
          interrupter.finish()
      except AttributeError, e:
        raise TestException('Missing property %s on %s'%(propName,str(obj)),e)
      except NonErrors:
        raise
      except (TestException, AssertionError, ReturnValue):
        raise
      except Exception, e:
        raise TestException('Getting %s on %s' % (propName,str(obj)), e)

    # Write to variable
    #
    if testNode.hasAttribute('var'):
      self.scope[testNode.getAttribute('var')]= value


  def setProperty(self, testNode):
    obj= self.ueval(testNode.getAttribute('obj'))
    propName= testNode.tagName
    value= self.ueval(testNode.getAttribute('value'))

    # Check for the existance of property first - DOM settable properties must
    # gettable, but Python does not enforce this restriction explicitly.
    #
    try:
      has= hasattr(obj, propName)
    except NonErrors:
      raise
    except (TestException, AssertionError, ReturnValue):
      raise
    except Exception, e:
      raise TestException('Broken %s on %s' % (propName,str(obj)), e)
    if not has:
      raise TestException('Missing property %s on %s' % (propName, str(obj)),
        AttributeError()
      )

    # Attempt to write to property
    #
    interrupter= Interrupter()
    try:
      interrupter.start()
      try:
        setattr(obj, propName, value)
      finally:
        interrupter.finish()
    except NonErrors:
      raise
    except Exception, e:
      raise TestException('Setting %s on %s' % (propName,str(obj)), e)


  def makeAssertion(self, testNode):
    assertContents= testNode.getElementsByTagName('*')
    assertType= testNode.tagName[6].lower()+testNode.tagName[7:]  
    if len(assertContents)>0:
      actual= self.checkCondition(assertContents[0])
    else:
      actual= self.getOneOf(testNode, ACTUALS)
      if testNode.hasAttribute('bitmask'):
        actual= actual & int(testNode.getAttribute('bitmask'))
    expected= self.getOneOf(testNode, EXPECTEDS)
    if testNode.hasAttribute('isAbsolute'):
      ab= self.ueval(testNode.getAttribute('isAbsolute'))
      if ab and expected is not None:
        ext= self.implementation.extension
        path= os.path.join(self.filesPath, expected+ext)
        expected= 'file:'+urllib.pathname2url(path)
    cs= True
    if testNode.hasAttribute('ignoreCase'):
      cs= not self.ueval(testNode.getAttribute('ignoreCase'))
      if cs is None:
        cs= self.implementation.contentType!='text/html'
    if not CONDITIONS[assertType](actual, expected, cs):
      if expected is not None:
        raise AssertionError('Assertion %s failed. Expected %s, got %s' % (
          testNode.getAttribute('id'), sstr(expected), sstr(actual)
        ))
      else:
        raise AssertionError('Assertion %s failed. Got %s' % (
          testNode.getAttribute('id'), actual
        ))


  def exceptionAssertion(self, testNode):
    assertContents= testNode.getElementsByTagName('*')
    requiredException= None
    if len(assertContents)>0:
      if assertContents[0].tagName in EXCEPTIONS:
        requiredException= EXCEPTIONS.index(assertContents[0].tagName)
        assertContents= assertContents[0].childNodes
    try:
      self.process(assertContents)
    except TestException, e:
      if requiredException is not None:
        code= getattr(e.exception, 'code', None)
        if code is not None and code>=len(EXCEPTIONS):
          code= '?'
        if code!=requiredException:
          raise AssertionError('Assertion %s failed. Expected %s, got %s (%s, %s)'%(
            testNode.getAttribute('id'), EXCEPTIONS[requiredException],
            str(code), e.exception.__class__.__name__, str(e.exception)
          ))
    else:
      if requiredException is not None:
        raise AssertionError('Assertion %s failed. Expected %s, got none' % (
          testNode.getAttribute('id'), EXCEPTIONS[requiredException]
        ))
      else:
        raise AssertionError('Assertion %s failed. Exception didn\'t occur' %
          testNode.getAttribute('id')
        )


  def readVar(self, testNode):
    value= None
    varType= testNode.getAttribute('type')

    # Initialise complex types
    #
    if varType in COMPLEXOBJECTS.keys():
      value= COMPLEXOBJECTS[varType]()
      for child in testNode.childNodes:
        if child.nodeType==child.ELEMENT_NODE:
          propType= child.tagName
          if propType=='member':
            value.append(self.ueval(getTextContent(child)))
          elif propType=='var':
            (propName, propValue)= self.readVar(child)
            setattr(value, propName, propValue)
          elif propType in METHODS.keys():
            value.setMethod(propType, TSMethod(value, child, self))
          elif propType in PROPERTIES:
            for grandchild in child.childNodes:
              if grandchild.nodeType==child.ELEMENT_NODE:
                gsName= grandchild.tagName
                if gsName=='get':
                  value.setGetter(propType, TSMethod(value, grandchild, self))
                elif gsName=='set':
                  value.setSetter(propType, TSMethod(value, grandchild, self))
                else:
                  raise ValueError('Unknown TSML property child %s' % gsName)
          else:
            raise ValueError('Unknown TSML property element %s' % propType)

    # Initialise simple types
    #
    else:
      if testNode.hasAttribute('value'):
        value= self.ueval(testNode.getAttribute('value'))
      if varType in SIMPLEOBJECTS.keys():
        value= SIMPLEOBJECTS[varType](value)

    return (testNode.getAttribute('name'), value)


  def ifCondition(self, testNode):
    conditionNode= None
    elseNode= None
    for child in testNode.childNodes:
      if child.nodeType==child.ELEMENT_NODE and conditionNode is None:
        conditionNode= child
      if child.nodeType==child.ELEMENT_NODE and child.tagName=='else':
        elseNode= child
    if self.checkCondition(conditionNode):
      contents= list(testNode.childNodes)
      contents.remove(conditionNode)
      if elseNode is not None:
        contents.remove(elseNode)
      self.process(contents)
    elif elseNode is not None:
      self.process(elseNode.childNodes)


  def whileLoop(self, testNode):
    conditionNode= testNode.getElementsByTagName('*')[0]
    contents= list(testNode.childNodes)
    contents.remove(conditionNode)
    while self.checkCondition(conditionNode):
      self.process(contents)


  def forLoop(self, testNode):
    member= testNode.getAttribute('member')
    collection= self.ueval(testNode.getAttribute('collection'))
    if hasattr(collection, 'item'):
      collectionList= []
      for ix in range(collection.length):
        collectionList.append(collection.item(ix))
    else:
      try:
        collectionList= list(collection)
      except NonErrors:
        raise
      except Exception, e:
        raise TestException('Reading list %s' % collection, e)
    for self.scope[member] in collectionList:
      self.process(testNode.childNodes)

  def tryBlock(self, testNode):
    catches= []
    others= []
    for child in testNode.childNodes:
      if child.nodeType==child.ELEMENT_NODE and child.tagName=='catch':
        for grandchild in child.childNodes:
          if grandchild.nodeType==child.ELEMENT_NODE:
            catches.append(grandchild)
      else:
        others.append(child)
    try:
      self.process(others)
    except TestException, e:
      for catch in catches:
        if catch.tagName!='ImplementationException':
          if hasattr(e.exception, 'code'):
            if e.exception.code==EXCEPTIONS.index(catch.getAttribute('code')):
              break
        if catch.tagName=='ImplementationException':
          break
      else:
        raise # exception had no matching <catch>
      self.process(catch.childNodes)


  def checkCondition(self, condNode):
    # If the condition is <not>, look inside it and invert the result
    #
    if condNode.tagName=='not':
      for child in condNode.childNodes:
        if child.nodeType==child.ELEMENT_NODE:
          return not self.checkCondition(child)

    # If the condition is an operator like <or>, recurse into each subcondition
    #
    if CONDITIONOPS.has_key(condNode.tagName):
      results= []
      for child in condNode.childNodes:
        if child.nodeType==child.ELEMENT_NODE:
          results.append(self.checkCondition(child))
      return reduce(CONDITIONOPS[condNode.tagName], results, False)

    if condNode.tagName=='contentType':
      actual= self.implementation.contentType
      expected= condNode.getAttribute('type')
    else:
      if condNode.tagName=='implementationAttribute':
        actual= self.implementation.getImplementationAttribute(
          condNode.getAttribute('name')
        )
      else:
        actual= self.getOneOf(condNode, ACTUALS)
      expected= self.getOneOf(condNode, EXPECTEDS)

    cs= True
    if condNode.hasAttribute('ignoreCase'):
      cs= not self.ueval(condNode.getAttribute('ignoreCase'))
      if cs is None:
        cs= self.implementation.contentType!='text/html'
    return CONDITIONS[condNode.tagName](actual, expected, cs)


  def ueval(self, expr):
    """ Evaluate an expression string. TSML expressions are compatible with
        Python except that in pre-2.3 Pythons Unicode characters can't be
        included directly. Assuming they are in a string literal, encode them in
        \u format and u-prefix the literal.
    """
    if type(expr)==type(u'') and expr[:1]=='"':
      ascii= 'u'
      for char in expr:
        if ord(char)>=128:
          ascii= ascii+('\\u%04x' % ord(char))
        else:
          ascii= ascii+str(char)
      expr= ascii
    if self.globalScope is None:
      value= eval(expr, self.scope)
    else:
      value= eval(expr, self.globalScope, self.scope)
    return value

  def getOneOf(self, node, attrs):
    """ Return the evaluated contents of any of the attributes specified in a
        list, or None, if the element has no such attributes.
    """
    for attr in attrs:
      if node.hasAttribute(attr):
        return self.ueval(node.getAttribute(attr))
    return None


class TSMethod:
  """ Object representing a test-created method in a test-created object. If
      it gets called (either by the test or by callback from the DOM), it
      passes its body node back to the Tester to run, with a local scope
      containing arguments and object members.
  """
  def __init__(self, obj, node, tester):
    self.obj= obj
    self.node= node
    self.tester= tester
  def __call__(self, *args):
    methodName= self.node.tagName
    if methodName=='get':
      argNames= []
    elif methodName=='set':
      argNames= ['value']
    else:
      argNames= METHODS[methodName]
    if len(argNames)!=len(args):
      raise TypeError('TSMethod %s takes exactly %d arguments, %d given' % (
        methodName, len(argNames), len(args)
      ))
    scope= self.obj.__dict__

    # Put method arguments in the object's scope temporarily so we can have a
    # a single shared local scope (as TSML does not use self.member)
    #
    for ix in range(len(args)):
      if scope.has_key(argNames[ix]):
        raise NameError('Argument name %s clashes with instance member' %
          argNames[ix]
        )
      scope[argNames[ix]]= args[ix]
      # special case, n and nodeArg again
      if argNames[ix]=='nodeArg':
        scope['n']= args[ix]

    # Replace tester's local scope
    #
    if self.tester.globalScope is None:
      oldScope= None
      self.tester.globalScope= self.tester.scope
      self.tester.scope= scope
    else:
      oldScope= self.tester.scope
      self.tester.scope= scope

    # Interpret method body. Get a <return> value if there is one.
    #
    try:
      self.tester.process(self.node.childNodes)
    except ReturnValue, e:
      value= e.value
    else:
      value= None

    # Clean up
    #
    for argName in argNames:
      del scope[argName]
    if oldScope is None:
      self.tester.scope= self.tester.globalScope
      self.tester.globalScope= None
    else:
      self.tester.scope= oldScope

    return value


def getTextContent(node):
  """ Get the textual content of a node - we can't rely on the DOM Level 3
      textContent property being available in the working-implementation.
  """
  textContent= ''
  for child in node.childNodes:
    if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE):
      textContent= textContent+child.data
    if child.nodeType in (child.ENTITY_REFERENCE_NODE, child.ELEMENT_NODE):
      textContent= textContent+getTextContent(child)
  return textContent

