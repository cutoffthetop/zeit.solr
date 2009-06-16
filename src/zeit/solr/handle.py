import httplib


class SolrHandle():

    def search_data(self):
        conn = httplib.HTTPConnection(self.url)
        conn.putrequest(
            'GET',
            '/solr/select/?q=foo&version=2.2&start=0&rows=10&indent=on'
        )
        conn.endheaders()
        self.response = conn.getresponse()
        
    def push_data(self, data):
        conn = httplib.HTTPConnection(self.url)
        conn.putrequest('POST', '/solr/update/')
        conn.putheader('content-length', str(len(data)))
        conn.putheader('content-type', 'text/xml; charset=UTF-8')
        conn.endheaders()
        conn.send(data)
        self.response = conn.getresponse()

