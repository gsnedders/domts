""" Python Document Object Model Test Suite. Interprets test suites from the
    W3C DOMTS project and carries them out against known Python DOM
    implementations. Requires Python 1.6 or later (as it uses Unicode and
    string methods).
"""

__all__= ['implementations', 'inbuilts', 'interfaces', 'interpreter', 'runSuite']
__version__= '0.5'

import os, sys
from implementations import *
from interpreter import *

def runSuite(suitePath, testImp, workImp):
  """ Run a suite of tests, given the filename of the suite or test document.
      Test a particular named implementation, using a second named
      implementation to do internal XML-related tasks. Omit either for a
      default DOM. Return a list of (testName, passedFlag, skippedFlag,
      failInfo) tuples.
  """
  workImp.beginWork()
  suiteDoc= workImp.parseFile(suitePath)
  basePath= os.path.dirname(suitePath)
  filesPath= os.path.join(basePath, 'files')
  tester= Tester(testImp, filesPath)
  try:
    workImp.setImplementationAttribute('expandEntityReferences', 1)
  except NotImplementedError:
    pass

  if suiteDoc.documentElement.nodeName=='test':
    testImp.beginTest()
    return [tester.runTest(suiteDoc)]
  elif suiteDoc.documentElement.nodeName=='suite':
    results= []
    for member in suiteDoc.getElementsByTagName('suite.member'):
      try:
        workImp.beginWork()
        testPath= os.path.join(basePath, member.getAttribute('href'))
        testDoc= workImp.parseFile(testPath)
        if testDoc.documentElement.tagName=='test':
          testImp.beginTest()
          results.append(tester.runTest(testDoc))
      except:
        sys.stderr.write('Test %s died...\n' % testPath)
        raise
    return results
  else:
    raise Exception('Unknown XML file, not test or suite of tests')
