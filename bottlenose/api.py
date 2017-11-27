# Copyright 2012-2017 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

try:
    from urllib import quote as urllib_quote
except ImportError:
    # Python 3
    from urllib.parse import quote as urllib_quote
    unicode = str


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
    'CA': ('webservices.amazon.ca', 'xml-ca.amznxslt.com'),
    'CN': ('webservices.amazon.cn', 'xml-cn.amznxslt.com'),
    'DE': ('webservices.amazon.de', 'xml-de.amznxslt.com'),
    'ES': ('webservices.amazon.es', 'xml-es.amznxslt.com'),
    'FR': ('webservices.amazon.fr', 'xml-fr.amznxslt.com'),
    'IN': ('webservices.amazon.in', 'xml-in.amznxslt.com'),
    'IT': ('webservices.amazon.it', 'xml-it.amznxslt.com'),
    'JP': ('webservices.amazon.co.jp', 'xml-jp.amznxslt.com'),
    'UK': ('webservices.amazon.co.uk', 'xml-uk.amznxslt.com'),
    'US': ('webservices.amazon.com', 'xml-us.amznxslt.com'),
    'BR': ('webservices.amazon.com.br', 'xml-br.amznxslt.com'),
    'MX': ('webservices.amazon.com.mx', 'xml-mx.amznxslt.com')
}

log = logging.getLogger(__name__)


def _quote_query(query):
    """Turn a dictionary into a query string in a URL, with keys
    in alphabetical order."""
    return "&".join("%s=%s" % (
        k, urllib_quote(
            unicode(query[k]).encode('utf-8'), safe='~'))
            for k in sorted(query))


class AmazonError(Exception):
    pass


class AmazonCall(object):
    def __init__(self, AWSAccessKeyId=None, AWSSecretAccessKey=None,
            AssociateTag=None, Operation=None, Version="2013-08-01", Region=None,
            Timeout=None, MaxQPS=None, Parser=None,
            CacheReader=None, CacheWriter=None,
            ErrorHandler=None,
            _last_query_time=None):

        self.AWSAccessKeyId = (AWSAccessKeyId or
                               os.environ.get('AWS_ACCESS_KEY_ID'))
        if self.AWSAccessKeyId is None:
            raise TypeError("AWSAccessKeyId is not defined.")

        self.AWSSecretAccessKey = (AWSSecretAccessKey or
                                   os.environ.get('AWS_SECRET_ACCESS_KEY'))
        if self.AWSSecretAccessKey is None:
            raise TypeError("AWSSecretAccessKey is not defined.")

        self.AssociateTag = (AssociateTag or
                             os.environ.get('AWS_ASSOCIATE_TAG'))
        if self.AssociateTag is None:
            raise TypeError("AssociateTag is not defined.")

        self.CacheReader = CacheReader
        self.CacheWriter = CacheWriter
        self.ErrorHandler = ErrorHandler
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
                              ErrorHandler=self.ErrorHandler,
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

        # convert unicode to UTF8 bytes for hmac library
        if type(self.AWSSecretAccessKey) is unicode:
            self.AWSSecretAccessKey = self.AWSSecretAccessKey.encode('utf-8')

        if type(data) is unicode:
            data = data.encode('utf-8')

        # calculate sha256 signature
        digest = hmac.new(self.AWSSecretAccessKey, data, sha256).digest()

        # base64 encode and urlencode
        if sys.version_info[0] == 3:
            signature = urllib.parse.quote(b64encode(digest))
        else:
            signature = urllib.quote(b64encode(digest))

        return ("https://" + service_domain + "/onca/xml?" +
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

        return "https://" + service_domain + "/onca/xml?" + _quote_query(query)

    def _call_api(self, api_url, err_env):
        """urlopen(), plus error handling and possible retries.

        err_env is a dict of additional info passed to the error handler
        """
        while True:  # may retry on error
            api_request = urllib2.Request(
                api_url, headers={"Accept-Encoding": "gzip"})

            log.debug("Amazon URL: %s" % api_url)

            try:
                if self.Timeout and sys.version[:3] in ["2.4", "2.5"]:
                    # urllib2.urlopen() doesn't accept timeout until 2.6
                    old_timeout = socket.getdefaulttimeout()
                    try:
                        socket.setdefaulttimeout(self.Timeout)
                        return urllib2.urlopen(api_request)
                    finally:
                        socket.setdefaulttimeout(old_timeout)
                else:
                    # the simple way
                    return urllib2.urlopen(api_request, timeout=self.Timeout)
            except:
                if not self.ErrorHandler:
                    raise

                exception = sys.exc_info()[1]  # works in Python 2 and 3
                err = {'exception': exception}
                err.update(err_env)
                if not self.ErrorHandler(err):
                    raise

    def __call__(self, **kwargs):
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

        # make the actual API call
        response = self._call_api(api_url,
                                  {'api_url': api_url, 'cache_url': cache_url})

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
            self.CacheWriter(cache_url, response_text)

        # parse and return it
        return self._maybe_parse(response_text)


class Amazon(AmazonCall):
    def __init__(self, AWSAccessKeyId=None, AWSSecretAccessKey=None,
            AssociateTag=None, Operation=None, Version="2013-08-01",
            Region="US", Timeout=None, MaxQPS=None, Parser=None,
            CacheReader=None, CacheWriter=None, ErrorHandler=None):
        """Create an Amazon API object.

        AWSAccessKeyId: Your AWS Access Key, sent with API queries. If not
                        set, will be automatically read from the environment
                        variable $AWS_ACCESS_KEY_ID
        AWSSecretAccessKey: Your AWS Secret Key, used to sign API queries. If
                            not set, will be automatically read from the
                            environment variable $AWS_SECRET_ACCESS_KEY
        AssociateTag: Your "username" for the Amazon Affiliate program,
                      sent with API queries.
        Version: API version. The default should work
        Region: ccTLD you want to search for products on (e.g. 'UK'
                for amazon.co.uk). Must be uppercase. Default is 'US'.
        Timeout: optional timeout for queries
        MaxQPS: optional maximum queries per second. If we've made an API call
                on this object more recently that 1/MaxQPS, we'll wait
                before making the call. Useful for making batches of queries.
                You generally want to set this a little lower than the
                max (so 0.9, not 1.0).
        Parser: a function that takes the raw API response (XML in a
                bytestring) and returns a more convenient object of
                your choice; if set, API calls will pass the response through
                this
        CacheReader: Called before attempting to make an API call.
                     A function that takes a single argument, the URL that
                     would be passed to the API, minus auth information,
                     and returns a cached version of the (unparsed) response,
                    or None
        CacheWriter: Called after a successful API call. A function that
                     takes two arguments, the same URL passed to
                     CacheReader, and the (unparsed) API response.
        ErrorHandler: Called after an unsuccessful API call, with a
                      dictionary containing these values:
                          exception: the exception (an HTTPError or URLError)
                          api_url: the url called
                          cache_url: the url used for caching purposes
                                     (see CacheReader above)
                      If this returns true, the call will be retried
                      (you generally want to wait some time before
                      returning, in this case)
        """
        # Operation is for internal use by AmazonCall.__getattr__()

        AmazonCall.__init__(self, AWSAccessKeyId, AWSSecretAccessKey,
                            AssociateTag, Operation, Version=Version,
                            Region=Region, Timeout=Timeout,
                            MaxQPS=MaxQPS, Parser=Parser,
                            CacheReader=CacheReader,
                            CacheWriter=CacheWriter,
                            ErrorHandler=ErrorHandler)


__all__ = ["Amazon", "AmazonError"]
