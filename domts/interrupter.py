""" domts.interrupter: watchdog thread to stop faulty DOM implementations
    hanging the tests in an infinite loop. Unfortunately there is no portable
    way to kill a thread in Python; the best we can do is print an error
    message to provoke the user into pressing Ctrl-C.
"""

__all__= ['Interrupter']

import sys, threading
try: True
except NameError: globals()['True'],globals()['False']= not None, not not None

# Timeout for single call in seconds
#
TIMEOUT= 15

class Interrupter(threading.Thread):
  def __init__(self):
      threading.Thread.__init__(self)
      self.finished= threading.Event()
      self.interrupted= threading.Event()
  def finish(self):
    self.finished.set()
    if self.interrupted.isSet():
      sys.stderr.write('Test aborted. Continuing suite.\n')
      raise UnresponsiveDOMTimeoutInterrupt()
  def run(self):
    self.finished.wait(TIMEOUT)
    if not self.finished.isSet():
      self.interrupted.set()
      sys.stderr.write(
        'Probable infinite loop in implementation. Press Ctrl-C to abort.\n'
      )


class UnresponsiveDOMTimeoutInterrupt(Exception):
  pass