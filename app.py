from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, threading
from core import evaluate, demo, ValidationError
ROOT=Path(__file__).parent
LOCK=threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def setup(self):
        super().setup()
        self.connection.settimeout(15)
    def trusted(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
    def reply(self,status,body,kind='application/json'):
        raw=json.dumps(body).encode() if kind=='application/json' else body
        self.send_response(status)
        self.send_header('Content-Type',kind+'; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if not self.trusted(): return self.reply(403,{'error':'Invalid host.'})
        files={'/':('index.html','text/html'),'/style.css':('style.css','text/css'),'/app.js':('app.js','text/javascript')}
        if self.path not in files: return self.reply(404,{'error':'Not found.'})
        name,kind=files[self.path]
        self.reply(200,(ROOT/'static'/name).read_bytes(),kind)
    def do_POST(self):
        if not self.trusted() or self.headers.get('Origin')!='http://'+self.headers.get('Host',''):
            return self.reply(403,{'error':'Only same-origin requests allowed.'})
        if self.headers.get('Content-Type')!='application/json': return self.reply(415,{'error':'Use JSON.'})
        if self.path not in ('/api/demo','/api/evaluate'): return self.reply(404,{'error':'Not found.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=8500000: raise ValidationError('Request missing or too large.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValidationError('Expected an object.')
        except (ValueError,TimeoutError): return self.reply(400,{'error':'Invalid or oversized request.'})
        if not LOCK.acquire(blocking=False): return self.reply(409,{'error':'Another evaluation is running.'})
        try:
            if self.path=='/api/demo':
                if data: raise ValidationError('Demo accepts only the fixed fictional example.')
                result=demo()
            else: result=evaluate(data)
            self.reply(200,result)
        except ValidationError as exc: self.reply(400,{'error':str(exc)})
        except Exception: self.reply(500,{'error':'Evaluation failed. No report accepted; earlier Azure requests may still be billable.'})
        finally: LOCK.release()
if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',8082),Handler)
    print('Heuristic Foundry Lab: http://127.0.0.1:8082')
    server.serve_forever()
