import sys
from restful_lib import Connection
import pprint
import json

class Client(object):
    def __init__(self, server, search='/search', index='/index', debug=0):
        
        self.server = server
        self.search = search
        self.index  = index
        
        # docs: 
        # http://code.google.com/p/python-rest-client/wiki/Using_Connection
        self.ua = Connection(server)
        
        # interrogate server
        resp = self.ua.request_get("/")
        # pprint.pprint(resp)
        paths = json.loads(resp['body'])
        self.search_uri = paths['search']
        self.index_uri  = paths['index']
        self.fields     = paths['fields']
        self.facets     = paths['facets']

    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return pprint.pformat(vars(self))

    def add(self, doc, uri=None, content_type=None):
        print "adding to index: " + doc
