""" domts.imitation: pretend to be a remote web server supporting GET and
    PUT requests, for DOM Level 3 LS tests.
"""

import threading, BaseHTTPServer
__all__= ['imitate', 'PORT']

# Arbitrary port number to run the server on
#
PORT= 9857

memory= {}

def imitate():
  serve= BaseHTTPServer.HTTPServer(('', PORT), Imitation).serve_forever
  imitation= threading.Thread(None, serve)
  imitation.setDaemon(True)
  imitation.start()

class Imitation(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    if memory.has_key(self.path):
      self.send_response(200)
      self.send_header('Content-Type', 'text/xml')
      self.end_headers()
      self.wfile.write(memory[self.path])
      self.wfile.close()
    else:
      self.send_error(404)
  def do_PUT(self):
    length= int(self.headers.getheader('Content-Length', '0'))
    memory[self.path]= self.rfile.read(length)
    self.send_response(200)
    self.send_header('Content-Type', 'text/plain')
    self.end_headers()
    self.wfile.write('OK')
    self.wfile.close()

  def log_request(a= None, b= None):
    pass
