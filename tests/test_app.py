import base64, copy, io, json, threading, unittest, urllib.request, urllib.error
from unittest.mock import patch
from PIL import Image
import core
from app import Handler, ThreadingHTTPServer

def sample():
    stream=io.BytesIO();Image.new('RGB',(20,20),'white').save(stream,format='PNG')
    return {'task':'Choose a plan','audience':'New customers','consent':True,'screens':[{'name':'plan.png','data':'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()}]}

def result(role):
    return {'coverage':[{'heuristic':h,'status':'not_assessable','reason':'Not visible in supplied state.'} for h in core.ROLES[role]],'findings':[]}

class CoreTests(unittest.TestCase):
    def test_image_hash(self):
        self.assertEqual(core.prepare(sample())['screens'][0]['id'],'S1')
        self.assertEqual(len(core.prepare(sample())['screens'][0]['sha256']),64)
    def test_invalid_image(self):
        x=sample();x['screens'][0]['data']='data:image/png;base64,YWJj'
        with self.assertRaises(core.ValidationError):core.prepare(x)
    def test_mime_mismatch(self):
        x=sample();x['screens'][0]['data']=x['screens'][0]['data'].replace('image/png','image/jpeg')
        with self.assertRaises(core.ValidationError):core.prepare(x)
    def test_screen_limit(self):
        x=sample();x['screens']*=4
        with self.assertRaises(core.ValidationError):core.prepare(x)
    def test_missing_context(self):
        x=sample();x['task']=''
        with self.assertRaises(core.ValidationError):core.prepare(x)
    def test_endpoint_restrictions(self):
        for e in ['http://a.openai.azure.com/openai/v1','https://evil.com/openai/v1','https://a.openai.azure.com.evil.com/openai/v1','https://a.openai.azure.com/openai/v1?secret=x']:
            with self.assertRaises(core.ValidationError):core.endpoint(e)
        self.assertEqual(core.endpoint('https://demo.openai.azure.com/openai/v1/'),'https://demo.openai.azure.com/openai/v1/responses')
    def test_consent_before_call(self):
        x=sample();x['consent']=False
        with self.assertRaises(core.ValidationError):core.evaluate(x,lambda *a:self.fail('No call permitted'))
    def test_three_roles_and_image_input(self):
        calls=[]
        def fake(instructions,content):
            role=list(core.ROLES)[len(calls)];calls.append(content)
            return result(role),{'total_tokens':10}
        out=core.evaluate(sample(),fake)
        self.assertEqual(len(calls),3)
        self.assertEqual(calls[0][-1]['type'],'input_image')
        self.assertNotIn('data',out['screens'][0])
        self.assertEqual(sum(len(r['coverage']) for r in out['reviews']),10)
    def test_unknown_screen(self):
        r=copy.deepcopy(core.demo()['reviews'][0]);r['findings'][0]['screen_id']='S99'
        with self.assertRaises(core.ValidationError):core.validate_review(r,'Interaction reviewer',{'S1'})
    def test_severity_bounds(self):
        r=copy.deepcopy(core.demo()['reviews'][0]);r['findings'][0]['severity']=True
        with self.assertRaises(core.ValidationError):core.validate_review(r,'Interaction reviewer',{'S1'})
    def test_coverage_agrees(self):
        r=copy.deepcopy(core.demo()['reviews'][0]);r['findings']=[]
        with self.assertRaises(core.ValidationError):core.validate_review(r,'Interaction reviewer',{'S1'})
    def test_coverage_unique(self):
        r=result('Interaction reviewer');r['coverage'][1]=r['coverage'][0]
        with self.assertRaises(core.ValidationError):core.validate_review(r,'Interaction reviewer',{'S1'})
    def test_partial_failure_not_success(self):
        calls=[]
        def fake(*args):
            if calls:raise core.ValidationError('Failed second role')
            calls.append(1);return result('Interaction reviewer'),{}
        with self.assertRaises(core.ValidationError):core.evaluate(sample(),fake)
    def test_demo_explicit(self):
        self.assertEqual(core.demo()['mode'],'fictional_demo')
    def test_request_contract(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return json.dumps({'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'{"coverage": [], "findings": []}'}]}]}).encode()
        class Opener:
            def open(self,req,timeout):
                p=json.loads(req.data);selftest.assertFalse(p['store']);selftest.assertEqual(p['input'][0]['content'][0]['type'],'input_image');selftest.assertEqual(p['text']['format']['type'],'json_object');return Response()
        selftest=self
        with patch.dict('os.environ',{'FOUNDRY_ENDPOINT':'https://demo.openai.azure.com/openai/v1','FOUNDRY_API_KEY':'test','FOUNDRY_DEPLOYMENT':'vision'}),patch('urllib.request.build_opener',return_value=Opener()):
            self.assertEqual(core.request_model('Review',[{'type':'input_image','image_url':'data:image/png;base64,AA=='}])[0]['findings'],[])

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def req(self,path,data,origin=None):
        return urllib.request.Request(self.base+path,json.dumps(data).encode(),{'Content-Type':'application/json','Origin':origin or self.base})
    def test_home_and_csp(self):
        with urllib.request.urlopen(self.base) as r:self.assertIn("frame-ancestors 'none'",r.headers['Content-Security-Policy']);self.assertIn(b'Heuristic Foundry Lab',r.read())
    def test_demo_route(self):
        with urllib.request.urlopen(self.req('/api/demo',{})) as r:self.assertEqual(json.load(r)['mode'],'fictional_demo')
    def test_cross_origin(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(self.req('/api/demo',{},'https://evil.example'))
        self.assertEqual(cm.exception.code,403)
    def test_reject_custom_demo(self):
        with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(self.req('/api/demo',sample()))
    def test_no_arbitrary_files(self):
        with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(self.base+'/core.py')
if __name__=='__main__':unittest.main()
