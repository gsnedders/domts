""" domts.implementations: interfacing to testable DOM implementations
"""

__all__= ['IMPLEMENTATIONS']

import os, urllib
try: True
except NameError: globals()['True'],globals()['False']= not None, not not None
def dictadd(a, b):
  ab= a.copy()
  ab.update(b)
  return ab


class Implementation:
  """ Interface for implementation hooks. Concrete subclasses should:
      - set property implementation to DOMImplementation object
      - set property implementationName to string for command line interface
      - provide a ParseFile method to return a Document object for a filename
      and may:
      - change extension and contentType for HTML or SVG imps
      - add more implementation attributes to fixedAttributes
      - provide _get/_setImplementationAttribute for non-fixed attributes
      - put attribute-initialising code in beginTest
  """
  extension= '.xml'
  contentType= 'text/xml'
  def __init__(self):
    self.beginTest()
  def beginTest(self):
    pass
  def beginWork(self):
    pass
  def parseFile(self, path):
    raise NotImplementedError('Cannot parse files')
  def getImplementationAttribute(self, attr):
    if self.fixedAttributes.has_key(attr):
      return self.fixedAttributes[attr]
    return self._getImplementationAttribute(attr)
  def setImplementationAttribute(self, attr, value):
    if self.fixedAttributes.has_key(attr):
      if self.fixedAttributes[attr]!=value:
        raise NotImplementedError('Fixed implementationAttribute %s' % attr)
    else:
       self._setImplementationAttribute(attr, value)
  def _getImplementationAttribute(self, attr):
    raise NotImplementedError('Unknown implementationAttribute %s' % attr)
  def _setImplementationAttribute(self, attr, value):
    raise NotImplementedError(
      'implementationAttribute %s cannot be set to %s' % (attr, str(value))
    )

  # General immutable attributes. Python has a null type (None) and uses
  # signed numbers so these shouldn't be changed. I have no idea what
  # 'coalescing' is supposed to do, but it always seems to be set false.
  #
  fixedAttributes= {
    'hasNullString': True,
    'signed': True,
    'coalescing': False
  }


class Level3LSImplementation(Implementation):
  """ Base class for implementations that support DOM Level 3 LS methods to
      load and set configuration options on a parser.
  """
  def beginTest(self):
    self.parser= self.implementation.createLSParser(1, None)
    self.parser.domConfig.setParameter('cdata-sections', True)
    self.parser.domConfig.setParameter('entities', True)

  def beginWork(self):
    self.parser= self.implementation.createLSParser(1, None)
    self.parser.domConfig.setParameter('cdata-sections', False)
    self.parser.domConfig.setParameter('entities', False)

  def parseFile(self, path):
    return self.parser.parseURI('file:'+urllib.pathname2url(path))

  def _getImplementationAttribute(self, attr):
    if not self.attributeParameters.has_key(attr):
      raise NotImplementedError('Unknown implementationAttribute %s' % attr)
    (param, state)= self.attributeParameters[attr]
    value= self.parser.domConfig.getParameter(param)
    if not state:
      return not value
    return value

  def _setImplementationAttribute(self, attr, value):
    if not self.attributeParameters.has_key(attr):
      raise NotImplementedError('Unknown implementationAttribute %s' % attr)
    (param, state)= self.attributeParameters[attr]
    if param is not None:
      if not state:
        value= not value
      if not self.parser.domConfig.canSetParameter(param, value):
        raise NotImplementedError(
          'implementationAttribute %s cannot be set to %s' % (attr, str(value))
        )
      self.parser.domConfig.setParameter(param, value)

  attributeParameters= {
    'namespaceAware': ('namespaces', True),
    'validating': ('validate', True),
    'expandEntityReferences': ('entities', False),
    'ignoringElementContentWhitespace': ('element-content-whitespace', False),
    'ignoringComments': ('comments', False)
  }


# Concrete Implementation classes
#
class PxdomImplementation(Level3LSImplementation):
  """ Implementation hook for pxdom, using DOM Level 3 LS methods.
  """
  implementationName= 'pxdom'
  def __init__(self):
    try:
      import pxdom
    except ImportError:
      from pxtl import pxdom
    self.implementation= pxdom.getDOMImplementation('')
    Level3LSImplementation.__init__(self)
  attributeParameters= dictadd(Level3LSImplementation.attributeParameters, {
    'validating': ('pxdom-resolve-resources', True)
  })
  fixedAttributes= dictadd(Implementation.fixedAttributes, {
    'schemaValidating': False
  })

class MinidomImplementation(Implementation):
  """ Implementation hook for minidom, the DOM from the Python standard
      library.
  """
  implementationName= 'minidom'
  def __init__(self):
    import xml.dom.minidom
    self.module= xml.dom.minidom
    self.implementation= xml.dom.minidom.getDOMImplementation()
    Implementation.__init__(self)

  def parseFile(self, path):
    # In occasional versions (?) minidom wants to read the DTD, but looks
    # relative to the current directory instead of the document. Work around.
    #
    os.chdir(os.path.dirname(path))
    return self.module.parse(path)

  fixedAttributes= dictadd(Implementation.fixedAttributes, {
    'namespaceAware': True,
    'validating': False,
    'schemaValidating': False,
    'expandEntityReferences': True,
    'ignoringElementContentWhitespace': False,
    'ignoringComments': False # True for older versions
  })


class FourDOMImplementation(Implementation):
  """ Implementation hook for 4DOM, PyXML's extended DOM implementation.
  """
  implementationName= '4DOM'
  def __init__(self):
    import xml.dom.DOMImplementation
    import xml.dom.ext.reader.PyExpat
    self.parser= xml.dom.ext.reader.PyExpat.Reader()
    self.implementation= xml.dom.DOMImplementation.getDOMImplementation()
    Implementation.__init__(self)

    # Hack: versions of 4DOM up to now die if they see notations. Test if this
    # is the case with the implementation we have, and if so patch it into
    # ignoring them instead.
    #
    try:
      d= self.parser.fromString('<!DOCTYPE x [<!NOTATION n SYSTEM "n">]><x/>')
    except AttributeError:
      self.parser.notationDecl= doNothing
      self.parser.unparsedEntityDecl= doNothing

  def parseFile(self, path):
    return self.parser.fromUri('file:'+urllib.pathname2url(path))

  fixedAttributes= dictadd(Implementation.fixedAttributes, {
    'namespaceAware': True,
    'validating': True, # Actually, this just means external entities are ok
    'schemaValidating': False,
    'expandEntityReferences': True,
    'ignoringElementContentWhitespace': False,
    'ignoringComments': False
  })

def doNothing(a1= None, a2= None, a3= None, a4= None, a5= None, a6= None):
  pass


class DomletteImplementation(Implementation):
  """ Base class for implementations using 4Suite 1.0 Domlettes. Subclasses
      should set parser
  """
  def __init__(self):
    from Ft.Xml import InputSource
    self.factory = InputSource.DefaultFactory

  def parseFile(self, path):
    source= self.factory.fromUri('file:'+urllib.pathname2url(path))
    return self.parser(source)

  fixedAttributes= dictadd(Implementation.fixedAttributes, {
    'namespaceAware': True,
    'validating': True,
    'expandEntityReferences': True,
    'ignoringElementContentWhitespace': False,
    'ignoringComments': False
  })


class CDomletteImplementation(DomletteImplementation):
  implementationName= 'cDomlette'
  def __init__(self):
    from Ft.Xml.cDomlette import implementation, nonvalParse
    self.implementation= implementation
    self.parser= nonvalParse
    DomletteImplementation.__init__(self)


class FtMiniDomImplementation(DomletteImplementation):
  implementationName= 'FtMiniDom'
  def __init__(self):
    from Ft.Xml.FtMiniDom import implementation, nonvalParse
    self.implementation= implementation
    self.parser= nonvalParse
    DomletteImplementation.__init__(self)


class MicrodomImplementation(Implementation):
  """ Implementation hook for microdom, Twisted's minimal implementation.
  """
  implementationName= 'microdom'
  def __init__(self):
    import twisted.web.microdom
    self.module= twisted.web.microdom
    self.implementation= self # microdom has no DOMImplementation. Pretend.
    Implementation.__init__(self)

  def parseFile(self, path):
    return self.module.parseXML(path)

  def hasFeature(self, feature, version):
    return feature in ('XML', 'Core')

  fixedAttributes= dictadd(Implementation.fixedAttributes, {
    'namespaceAware': False,
    'validating': False,
    'expandEntityReferences': False,
    'ignoringElementContentWhitespace': False,
    'ignoringComments': False
  })


# Make a map of all the Implementation classes defined in this module, indexed
# by their names.
#
IMPLEMENTATIONS= {}
for x in globals().values():
  if hasattr(x, 'implementationName'):
    IMPLEMENTATIONS[x.implementationName.lower()]= x
