from base64 import b64encode
import gzip
import sys
import urllib
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
import hmac
import os
import time
import socket
import logging

from hashlib import sha256

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

# Python 2.4 compatibility
# http://code.google.com/p/boto/source/detail?r=1011
if sys.version[:3] == "2.4":
    # we are using an hmac that expects a .new() method.
    class Faker:
        def __init__(self, which):
            self.which = which
            self.digest_size = self.which().digest_size

        def new(self, *args, **kwargs):
            return self.which(*args, **kwargs)

    sha256 = Faker(sha256)


try:
    from exceptions import Exception
except ImportError:
    pass

SERVICE_DOMAINS = {
    'CA': ('ecs.amazonaws.ca', 'xml-ca.amznxslt.com'),
    'CN': ('webservices.amazon.cn', 'xml-cn.amznxslt.com'),
    'DE': ('ecs.amazonaws.de', 'xml-de.amznxslt.com'),
    'ES': ('webservices.amazon.es', 'xml-es.amznxslt.com'),
    'FR': ('ecs.amazonaws.fr', 'xml-fr.amznxslt.com'),
    'IT': ('webservices.amazon.it', 'xml-it.amznxslt.com'),
    'JP': ('ecs.amazonaws.jp', 'xml-jp.amznxslt.com'),
    'UK': ('ecs.amazonaws.co.uk', 'xml-uk.amznxslt.com'),
    'US': ('ecs.amazonaws.com', 'xml-us.amznxslt.com'),
}


def _quote_query(query):
    """Turn a dictionary into a query string in a URL, with keys
    in alphabetical order."""
    if sys.version_info[0] == 3:
        return "&".join("%s=%s" % (
            k, urllib.parse.quote(
                str(query[k]).encode('utf-8'), safe='~'))
                for k in sorted(query))
    else:
        return "&".join("%s=%s" % (
            k, urllib.quote(
                unicode(query[k]).encode('utf-8'), safe='~'))
                for k in sorted(query))


class AmazonError(Exception):
    pass


class AmazonCall(object):
    def __init__(self, AWSAccessKeyId=None, AWSSecretAccessKey=None,
            AssociateTag=None, Operation=None, Version=None, Region=None,
            Timeout=None, MaxQPS=None, Parser=None,
            CacheReader=None, CacheWriter=None,
            _last_query_time=None):

        self.AWSAccessKeyId = (AWSAccessKeyId or
                               os.environ.get('AWS_ACCESS_KEY_ID'))
        self.AWSSecretAccessKey = (AWSSecretAccessKey or
                                   os.environ.get('AWS_SECRET_ACCESS_KEY'))
        self.AssociateTag = (AssociateTag or
                             os.environ.get('AWS_ASSOCIATE_TAG'))
        self.CacheReader = CacheReader
        self.CacheWriter = CacheWriter
        self.MaxQPS = MaxQPS
        self.Operation = Operation
        self.Parser = Parser
        self.Version = Version
        self.Region = Region
        self.Timeout = Timeout

        # put this in a list so it can be shared between instances
        self._last_query_time = _last_query_time or [None]

    def signed_request(self):
        pass

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except:
            return AmazonCall(self.AWSAccessKeyId, self.AWSSecretAccessKey,
                              self.AssociateTag,
                              Operation=k, Version=self.Version,
                              Region=self.Region, Timeout=self.Timeout,
                              MaxQPS=self.MaxQPS, Parser=self.Parser,
                              CacheReader=self.CacheReader,
                              CacheWriter=self.CacheWriter,
                              _last_query_time=self._last_query_time)

    def _maybe_parse(self, response_text):
        if self.Parser:
            return self.Parser(response_text)
        else:
            return response_text


    def api_url(self, **kwargs):
        """The URL for making the given query against the API."""
        query = {
            'Operation': self.Operation,
            'Service': "AWSECommerceService",
            'Timestamp': time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            'Version': self.Version,
        }
        query.update(kwargs)

        query['AWSAccessKeyId'] = self.AWSAccessKeyId
        query['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                           time.gmtime())

        if self.AssociateTag:
            query['AssociateTag'] = self.AssociateTag

        service_domain = SERVICE_DOMAINS[self.Region][0]
        quoted_strings = _quote_query(query)

        data = "GET\n" + service_domain + "\n/onca/xml\n" + quoted_strings

        if sys.version_info[0] == 3:
            digest = hmac.new(
                bytes(self.AWSSecretAccessKey, encoding='utf-8'),
                bytes(data, encoding='utf-8'), sha256).digest()
            signature = urllib.parse.quote(b64encode(digest))
        else:
            digest = hmac.new(self.AWSSecretAccessKey, data, sha256).digest()
            signature = urllib.quote(b64encode(digest))

        return ("http://" + service_domain + "/onca/xml?" +
                quoted_strings + "&Signature=%s" % signature)

    def cache_url(self, **kwargs):
        """A simplified URL to be used for caching the given query."""
        query = {
            'Operation': self.Operation,
            'Service': "AWSECommerceService",
            'Version': self.Version,
        }
        query.update(kwargs)

        service_domain = SERVICE_DOMAINS[self.Region][0]

        return "http://" + service_domain + "/onca/xml?" + _quote_query(query)

    def __call__(self, **kwargs):
        log = logging.getLogger(__name__)

        if 'Style' in kwargs:
            raise AmazonError("The `Style` parameter has been discontinued by"
                              " AWS. Please remove all references to it and"
                              " reattempt your request.")

        cache_url = self.cache_url(**kwargs)

        if self.CacheReader:
            cached_response_text = self.CacheReader(cache_url)
            if cached_response_text is not None:
                return self._maybe_parse(cached_response_text)

        api_url = self.api_url(**kwargs)

        # throttle ourselves if need be
        if self.MaxQPS:
            last_query_time = self._last_query_time[0]
            if last_query_time:
                wait_time = 1 / self.MaxQPS - (time.time() - last_query_time)
                if wait_time > 0:
                    log.debug('Waiting %.3fs to call Amazon API' % wait_time)
                    time.sleep(wait_time)

            self._last_query_time[0] = time.time()

        # make the actual call
        api_request = urllib2.Request(
            api_url, headers={"Accept-Encoding": "gzip"})
        if self.Timeout:
            socket.setdefaulttimeout(self.Timeout)
        log.debug("Amazon URL: %s" % api_url)
        response = urllib2.urlopen(api_request)
        if self.Timeout:
            socket.setdefaulttimeout(None)

        # decompress the response if need be
        if sys.version_info[0] == 3:
            if "gzip" in response.info().get("Content-Encoding"):
                response_text = gzip.decompress(response.read())
            else:
                response_text = response.read()
        else:
            if "gzip" in response.info().getheader("Content-Encoding"):
                gzipped_file = gzip.GzipFile(fileobj=StringIO(response.read()))
                response_text = gzipped_file.read()
            else:
                response_text = response.read()

        # write it back to the cache
        if self.CacheWriter:
            # put this in a dictionary so we can add fields as needed
            response_info = {
                'data': response_text,
                'status_code': response.getcode(),
            }
            self.CacheWriter(cache_url, response_info)

        # parse and return it
        return self._maybe_parse(response_text)


class Amazon(AmazonCall):
    def __init__(self, AWSAccessKeyId=None, AWSSecretAccessKey=None,
            AssociateTag=None, Operation=None, Version="2011-08-01",
            Region="US", Timeout=None, MaxQPS=None, Parser=None,
            CacheReader=None, CacheWriter=None):

        AmazonCall.__init__(self, AWSAccessKeyId, AWSSecretAccessKey,
                            AssociateTag, Operation, Version=Version,
                            Region=Region, Timeout=Timeout,
                            MaxQPS=MaxQPS, Parser=Parser,
                            CacheReader=CacheReader,
                            CacheWriter=CacheWriter)


__all__ = ["Amazon", "AmazonError"]
