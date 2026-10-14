"""Loopback preview of research pairs using the existing built viewer."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
ROOT=Path(__file__).resolve().parents[2]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist'),**kwargs)
 def do_GET(self):
  path=urlparse(self.path).path
  if path=='/bank.json':
   data=json.dumps([{'path':f'2way_bank/pl16_reference/{n}.flyer','name':f'Two-way PL16 — {n}','push_limit':16,'blocks':30,'version':'verified-20261014','categories':['observer_only'],'speed_bps':1666/1000,'distance':1666,'ticks':10000} for n in ('A','B')]).encode()
   self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  elif path in ('/2way_bank/pl16_reference/A.flyer','/2way_bank/pl16_reference/B.flyer'):
   data=(ROOT/path.lstrip('/')).read_bytes();self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else:super().do_GET()
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8767),Handler).serve_forever()
