""" domts.interfaces: define which TSML elements are referring to which sorts
    of DOM interfaces.
"""

__all__= [
  'PROPERTIES', 'EXCEPTIONS', 'METHODS', 'COMPLEXOBJECTS', 'SIMPLEOBJECTS'
]

from inbuilts import OBJECTS, TestCreatedObject
def dictadd(a, b):
  ab= a.copy()
  ab.update(b)
  return ab

# All get/settable DOM properties.
#
PROPERTIES= [
  # level1/core
  'nodeType', 'nodeValue', 'nodeName', 'ownerDocument', 'firstChild',
  'lastChild', 'nextSibling', 'previousSibling', 'parentNode', 'childNodes',
  'attributes', 'name', 'value', 'specified', 'data', 'length', 'doctype',
  'implementation', 'documentElement', 'entities', 'notations', 'tagName',
  'target', 'notationName', 'publicId', 'systemId', 'code',
  # level2/core
  'prefix', 'localName', 'namespaceURI', 'ownerElement', 'internalSubset',
  # level2/events
  'type', 'currentTarget', 'eventPhase', 'bubbles', 'cancelable', 'timeStamp',
  # level3/core
  'schemaTypeInfo', 'isId', 'inputEncoding', 'xmlEncoding', 'xmlVersion',
  'xmlStandalone', 'strictErrorChecking', 'documentURI', 'domConfig',
  'baseURI', 'textContent', 'wholeText', 'isElementContentWhitespace',
  'typeInfo', 'typeName', 'typeNamespace', 'severity', 'relatedException',
  'relatedData', 'location', 'lineNumber', 'columnNumber', 'byteOffset',
  'utf16Offset', 'relatedNode', 'uri', 'parameterNames',
  # level3/ls
  'config', 'filter', 'async', 'busy', 'characterStream', 'byteStream',
  'encoding', 'stringData', 'certifiedText', 'type', 'whatToShow', 'input'
  'position', 'totalSize', 'newDocument', 'newLine',
  # TS-specific properties
  'allEvents', 'atEvents', 'bubbledEvents', 'capturedEvents'
]

# DOMException types, in order.
#
EXCEPTIONS= [
  'INDEX_SIZE_ERR', 'DOMSTRING_SIZE_ERR', 'HIERARCHY_REQUEST_ERR',
  'WRONG_DOCUMENT_ERR', 'INVALID_CHARACTER_ERR', 'NO_DATA_ALLOWED_ERR',
  'NO_MODIFICATION_ALLOWED_ERR', 'NOT_FOUND_ERR', 'NOT_SUPPORTED_ERR',
  'INUSE_ATTRIBUTE_ERR', 'INVALID_STATE_ERR', 'SYNTAX_ERR',
  'INVALID_MODIFICATION_ERR', 'NAMESPACE_ERR', 'INVALID_ACCESS_ERR',
  'VALIDATION_ERR', 'TYPE_MISMATCH_ERR'
]

# DOM methods and the correct order for their arguments.
#
METHODS= {
  # level1/core
  'appendChild':                 ['newChild'],
  'removeChild':                 ['oldChild'],
  'replaceChild':                ['newChild', 'oldChild'],
  'insertBefore':                ['newChild', 'refChild'],
  'cloneNode':                   ['deep'],
  'hasChildNodes':               [],
  'createElement':               ['tagName'],
  'createDocumentFragment':      [],
  'createTextNode':              ['data'],
  'createComment':               ['data'],
  'createCDATASection':          ['data'],
  'createProcessingInstruction': ['target', 'data'],
  'createAttribute':             ['name'],
  'createEntityReference':       ['name'],
  'hasFeature':                  ['feature', 'version'],
  'getAttribute':                ['name'],
  'hasAttribute':                ['name'],
  'setAttribute':                ['name', 'value'],
  'removeAttribute':             ['name'],
  'getAttributeNode':            ['name'],
  'setAttributeNode':            ['newAttr'],
  'removeAttributeNode':         ['oldAttr'],
  'getElementsByTagName':        ['tagname'],
  'normalize':                   [],
  'item':                        ['index'],
  'getNamedItem':                ['name'],
  'setNamedItem':                ['arg'],
  'removeNamedItem':             ['name'],
  'substringData':               ['offset', 'count'],
  'appendData':                  ['arg'],
  'insertData':                  ['offset', 'arg'],
  'deleteData':                  ['offset', 'count'],
  'replaceData':                 ['offset', 'count', 'arg'],
  'splitText':                   ['offset'],
  # level2/core
  'createDocumentType':          ['qualifiedName', 'publicId', 'systemId'],
  'createDocument':              ['namespaceURI', 'qualifiedName', 'doctype'],
  'createElementNS':             ['namespaceURI', 'qualifiedName'],
  'createAttributeNS':           ['namespaceURI', 'qualifiedName'],
  'getElementsByTagNameNS':      ['namespaceURI', 'localName'],
  'getNamedItemNS':              ['namespaceURI', 'localName'],
  'setNamedItemNS':              ['arg'],
  'removeNamedItemNS':           ['namespaceURI', 'localName'],
  'getAttributeNS':              ['namespaceURI', 'localName'],
  'setAttributeNS':              ['namespaceURI', 'qualifiedName', 'value'],
  'removeAttributeNS':           ['namespaceURI', 'localName'],
  'getAttributeNodeNS':          ['namespaceURI', 'localName'],
  'setAttributeNodeNS':          ['newAttr'],
  'hasAttributeNS':              ['namespaceURI', 'localName'],
  'importNode':                  ['importedNode', 'deep'],
  'getElementById':              ['elementId'],
  'hasAttributes':               [],
  'isSupported':                 ['feature', 'version'],
  # level2/events
  'createEvent':                 ['eventType'],
  'addEventListener':            ['type', 'listener', 'useCapture'],
  'removeEventListener':         ['type', 'listener', 'useCapture'],
  'dispatchEvent':               ['evt'],
  'handleEvent':                 ['evt'],
  'stopPropagation':             [],
  'preventDefault':              [],
  'initEvent':                   ['eventTypeArg', 'canBubbleArg',
                                  'cancelableArg'],
  # level3/core
  'adoptNode':                   ['source'],
  'normalizeDocument':           [],
  'renameNode':                  ['n', 'namespaceURI', 'qualifiedName'],
  'getFeature':                  ['feature', 'version'],
  'setIdAttribute':              ['name', 'isId'],
  'setIdAttributeNS':            ['namespaceURI', 'localName', 'isId'],
  'setIdAttributeNode':          ['idAttr', 'isId'],
  'compareDocumentPosition':     ['other'],
  'isSameNode':                  ['other'],
  'isEqualNode':                 ['arg'],
  'lookupNamespaceURI':          ['prefix'],
  'lookupPrefix':                ['namespaceURI'],
  'isDefaultNamespace':          ['namespaceURI'],
  'setUserData':                 ['key', 'data', 'handler'],
  'getUserData':                 ['key'],
  'replaceWholeText':            ['content'],
  'getDOMImplementation':        ['features'],
  'getDOMImplementationList':    ['features'],
  'getParameter':                ['name'],
  'setParameter':                ['name', 'value'],
  'canSetParameter':             ['name', 'value'],
  # level3/ls
  'createLSParser':              ['mode', 'schemaType'],
  'createLSSerializer':          [],
  'createLSInput':               [],
  'createLSOutput':              [],
  'parse':                       ['input'],
  'parseURI':                    ['uri'],
  'parseWithContext':            ['input', 'contextArg', 'action'],
  'abort':                       [],
  'write':                       ['nodeArg', 'destination'],
  'writeToURI':                  ['nodeArg', 'uri'],
  'writeToString':               ['nodeArg'],
  'startElement':                ['elementArg'],
  'acceptNode':                  ['nodeArg'],
  'resolveResource':             ['type', 'namespaceURI', 'publicId',
                                  'systemId', 'baseURI'],
  # level3/events
  'addEventListenerNS':          ['namespaceURI', 'type', 'listener',
                                  'useCapture', 'evtGroup'],
  'removeEventListenerNS':       ['namespaceURI', 'type', 'listener',
                                  'useCapture'],
  'hasEventListenerNS':          ['namespaceURI', 'type'],
  'willTriggerNS':               ['namespaceURI', 'type'],
  'canDispatch':                 ['namespaceURI', 'type'],
  'initEventNS':                 ['namespaceURI', 'eventTypeArg',
                                  'canBubbleArg', 'cancelableArg'],
  'isCustom':                    [],
  'isDefaultPrevented':          [],
  'isPropagationStopped':        [],
  'isImmediatePropagationStopped':[],
  'setDispatchState':            ['target', 'phase'],
  'stopImmediatePropagation':    [],
}


class LSCharacterStream:
  def __init__(self, value):
    if value is None:
      self.value= ''
    else:
      self.value= value
  def read(self):
    try:
      return self.value
    finally:
      self.value= ''
  def write(self, chars):
    self.value= self.value+chars

class LSByteStream(LSCharacterStream):
  def __init__(self, value):
    bytes= []
    if value is not None:
      for ix in range(0, len(value), 2):
        bytes.append(chr(eval('0x'+value[ix:ix+2])))
    self.value= ''.join(bytes)

# Simple objects initialised from TSML <var value> attrs
#
SIMPLEOBJECTS= {
  'LSReader': LSCharacterStream,
  'LSInputStream': LSByteStream,
  'LSWriter': LSCharacterStream,
  'LSOutputStream': LSByteStream
}


class EventMonitor:
  """ Predefined TS utility object. An EventListener that records all events
      passed to it.
  """
  def __init__(self):
    self.allEvents= []
    self.capturedEvents= []
    self.atEvents= []
    self.bubbledEvents= []
  def handleEvent(evt):
    self.allEvents.append(evt)
    [self.capturedEvents, self.atEvents, self.bubbledEvents
    ][evt.eventPhase-1].append(evt)

# Objects that tests can create, in addition to List and Collection which are
# defined in domts.inbuilts.
#
COMPLEXOBJECTS= dictadd(OBJECTS, {
  'EventListener': TestCreatedObject,
  'LSParserFilter': TestCreatedObject,
  'LSSerializerFilter': TestCreatedObject,
  'LSResourceResolver': TestCreatedObject,
  'EventMonitor':  EventMonitor
})
