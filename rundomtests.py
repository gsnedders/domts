#!/usr/bin/env python

from domts import runSuite, implementations

import sys, getopt

__usage__= 'use: rundomtests.py [--testdom=...] [--workdom=...] alltests.xml'

try:
  opts, args= getopt.getopt(sys.argv[1:], '', ['testdom=','workdom=','tempuri='])
except getopt.GetoptError, e:
  sys.stderr.write(__usage__)
  sys.exit(1)
if len(args)!=1:
  sys.stderr.write(__usage__)
  sys.exit(1)
testdom= 'minidom'
workdom= 'minidom'
for (opt, value) in opts:
  if opt=='--testdom':
    testdom= value
  elif opt=='--workdom':
    workdom= value
testimp= implementations.IMPLEMENTATIONS[testdom.lower()]()
workimp= implementations.IMPLEMENTATIONS[workdom.lower()]()

results= runSuite(args[0], testimp, workimp)

passed= []
failed= []
skipped= []
for result in results:
  if result[2]:
    skipped.append(result)
  elif result[1]:
    passed.append(result)
  else:
    failed.append(result)

if len(failed)==0 and len(skipped)==0:
  print 'PASSED ALL %d tests!' % len(passed)
else:
  print 'PASSED %d test%s' % (len(passed), ['s', ''][len(passed)==1])
if len(failed)!=0:
  print 'FAILED %d test%s:' % (len(failed), ['s', ''][len(failed)==1])
  for fail in failed:
    print '  %s: %s' % (fail[0], fail[3])
if len(skipped)!=0:
  print 'SKIPPED %d test%s:' % (len(skipped), ['s', ''][len(skipped)==1])
  for skip in skipped:
    print '  %s: %s' % (skip[0], skip[3])
