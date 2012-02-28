import sys
import os
from restful_lib import Connection
import pprint
import json

class Client(object):
    def __init__(self, server, search='/search', index='/index', debug=False):
        
        self.server = server
        self.search = search
        self.index  = index
        self.debug  = debug
        
        # docs: 
        # http://code.google.com/p/python-rest-client/wiki/Using_Connection
        self.ua = Connection(server)
        
        # interrogate server
        resp = self.ua.request_get("/")
        pprint.pprint(resp)
        paths = json.loads(resp['body'])
        self.searcher   = Connection(paths['search'])
        self.indexer    = Connection(paths['index'])
        self.fields     = paths['fields']
        self.facets     = paths['facets']

    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return pprint.pformat(vars(self))

    def _put_doc(self, doc, uri=None, content_type=None):
        print "adding to index: %s" % doc
        
        body_buf = "";
        
        if (isinstance(doc, Doc)):
            print "doc isa Dezi.Doc\n"
            body_buf = doc.as_string()
            if (uri == None):
                uri = doc.uri
            if (content_type == None):
                content_type = doc.mime_type
                
        elif (os.path.isfile(doc)):
            f = open(doc, 'r')
            body_buf = f.read()
            if (uri == None):
                uri = doc
                
        else:
            print "doc isa string\n"
            body_buf = doc
            if (uri == None):
                raise Exception("uri required")
            
        server_uri = '/' + uri
        if (self.debug):
            print("uri="+server_uri)
            print("body=%s"%body_buf)
            
        resp = self.indexer.request_post(
            server_uri, 
            body=body_buf, 
            headers={'Content-Type':content_type}
        )
        
        pprint.pprint(resp)
        return Response(resp)

    def add(self, doc, uri=None, content_type=None):
        return self._put_doc(doc, uri, content_type)
        
    def update(self, doc, uri=None, content_type=None):
        return self._put_doc(doc, uri, content_type)
        
    def delete(self, uri):
        resp = self.indexer.request_delete(uri)
        return Response(resp)
        
    def search(self, q):
        resp = self.searcher.request_get("/", args={'q':q})
        return Response(resp)
        

class Doc(object):
    def __init__( self, 
        mime_type=None, 
        summary=None, 
        title=None, 
        content=None, 
        uri=None, 
        mtime=None, 
        size=None,
        score=None ):
        
        self.mime_type = mime_type
        self.summary   = summary
        self.title     = title
        self.content   = content
        self.uri       = uri
        self.mtime     = mtime
        self.size      = size
        self.score     = score
        self.fields    = {}
        
    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return self.uri
                
    def as_string(self):
        if (len(self.fields)):
            return self.as_xml()
        else:
            return self.content
    
    def as_xml(self):
        xml = dict2xml({'doc':self.fields})
        return xml.display()
        
    def set_field(self, field, val):
        self.fields[field] = val
        self.mime_type = 'application/xml'


class Response(object):
    def __init__(self, http_resp):
        self.http_resp = http_resp
        
    def is_success(self):
        pprint.pprint(self.http_resp)
        if (self.http_resp['headers']['status'] == 200):
            return True
        else:
            return False
        
        
# from http://pynuggets.wordpress.com/2011/06/06/dict2xml-4/
from xml.dom.minidom import Document
import copy
class dict2xml(object):
    doc = Document()

    def __init__(self, structure):
        if len(structure) == 1:
            rootName = str(structure.keys()[0])
            self.root = self.doc.createElement(rootName)
            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName])

    def display(self):
        return self.doc.toprettyxml(indent=" ")

    def build(self, father, structure):
        if type(structure) == dict:
            for k in structure:
                tag = self.doc.createElement(k)
                father.appendChild(tag)
                self.build(tag, structure[k])

        elif type(structure) == list:
            grandFather = father.parentNode
            uncle = copy.deepcopy(father)
            for l in structure:
                self.build(father, l)
                grandFather.appendChild(father)
                father = copy.deepcopy(uncle)

        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)
