#!/usr/bin/env python

# include local python rest client lib
# not assuming this is installed already
# but might be in parallel dir (as it is for me)
import sys
sys.path.append("../python-rest-client")
sys.path.append(".")

import pprint
from TAP.Simple import *

import Dezi

plan(14)

client = Dezi.Client('http://localhost:5000', debug=False, username='foo', password='bar')

diag("testing Dezi pythong client version " + client.version )

# add/update a filesystem document to the index
resp = client.add('t/test.html')
#diag( resp.http_resp['headers']['status'] )
ok( resp.is_success(), "index fs success" )

# add/update an in-memory document to the index
html_doc = '<html><title>hello world</title><body>foo bar</body></html>'
resp = client.add( html_doc, 'foo/bar.html' )
ok( resp.is_success(), "index scalar_ref success" )

# add/update a Dezi.Doc to the index
dezi_doc = Dezi.Doc( uri = 't/test-dezi-doc.xml' )
f = open(dezi_doc.uri, 'r')
dezi_doc.content = f.read()
resp = client.add(dezi_doc)
ok( resp.is_success(), "index Dezi::Doc success" )

doc2 = Dezi.Doc( uri='auto/xml/magic' )
doc2.set_field( 'title', 'ima dezi doc' )
doc2.set_field( 'body', 'hello world!' )
resp = client.add(doc2)
ok( resp.is_success(), "auto XML success" )

# commit changes
resp = client.commit()
ok( resp.is_success(), "commit changes" )
eq_ok( resp.status(), '200', "/commit status == 200")

# remove a document from the index

resp = client.delete('foo/bar.html')
ok( resp.is_success(), "delete success" )

# search the index
response = client.get( q = 'dezi' )

#pprint.pprint(vars( response ), sys.stderr)

## iterate over results
for result in response.results:

    #pprint.pprint(vars( result ), sys.stderr )
    ok( result.uri, "get result uri %s" % result.uri )
    diag(
          "--\n uri: %s\n title: %s\n score: %s\n swishmime: %s\n" % (result.uri, 
          result.title, result.score, result.get_field('swishmime')[0],)
    )

# print stats
eq_ok( response.total, 3, "got 3 results" )
ok( response.search_time, "got search_time" )
ok( response.build_time,  "got build time" )
eq_ok( response.query, "dezi", "round-trip query string" )
#diag( response.query )
