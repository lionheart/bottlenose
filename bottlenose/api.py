from base64 import b64encode
import gzip
import sys
import urllib
import urllib2
import hmac
import time

from hashlib import sha256

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

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

from exceptions import Exception

SERVICE_DOMAINS = {
    'CA': ('ecs.amazonaws.ca', 'xml-ca.amznxslt.com'),
    'DE': ('ecs.amazonaws.de', 'xml-de.amznxslt.com'),
    'FR': ('ecs.amazonaws.fr', 'xml-fr.amznxslt.com'),
    'JP': ('ecs.amazonaws.jp', 'xml-jp.amznxslt.com'),
    'US': ('ecs.amazonaws.com', 'xml-us.amznxslt.com'),
    'UK': ('ecs.amazonaws.co.uk', 'xml-uk.amznxslt.com'),
}

class AmazonError(Exception):
    pass

class AmazonCall(object):
    def __init__(self, AWSAccessKeyId=None, AWSSecretAccessKey=None, \
            AssociateTag=None, Operation=None, Version="2010-11-01", Region="US"):
        self.AWSAccessKeyId = AWSAccessKeyId
        self.AWSSecretAccessKey = AWSSecretAccessKey
        self.Operation = Operation
        self.AssociateTag = AssociateTag
        self.Version = Version
        self.Region = Region

    def signed_request(self):
        pass

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except:
            return AmazonCall(self.AWSAccessKeyId, self.AWSSecretAccessKey, \
                    self.AssociateTag, Operation=k, Version=self.Version, Region=self.Region)

    def __call__(self, **kwargs):
        kwargs['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        kwargs['Operation'] = self.Operation
        kwargs['Version'] = self.Version
        kwargs['AWSAccessKeyId'] = self.AWSAccessKeyId
        kwargs['Service'] = "AWSECommerceService"

        if self.AssociateTag:
            kwargs['AssociateTag'] = self.AssociateTag

        if 'Style' in kwargs:
            service_domain = SERVICE_DOMAINS[self.Region][1]
        else:
            service_domain = SERVICE_DOMAINS[self.Region][0]

        keys = kwargs.keys()
        keys.sort()

        quoted_strings = "&".join("%s=%s" % (k, urllib.quote(unicode(kwargs[k]).encode('utf-8'), safe = '~')) for k in keys)

        data = "GET\n" + service_domain + "\n/onca/xml\n" + quoted_strings

        digest = hmac.new(self.AWSSecretAccessKey, data, sha256).digest()
        signature = urllib.quote(b64encode(digest))

        api_string = "http://" + service_domain + "/onca/xml?" + quoted_strings + "&Signature=%s" % signature
        api_request = urllib2.Request(api_string, headers={"Accept-Encoding": "gzip"})
        response = urllib2.urlopen(api_request)
        
        if "gzip" in response.info().getheader("Content-Encoding"):
            gzipped_file = gzip.GzipFile(fileobj=StringIO.StringIO(response.read()))
            response_text = gzipped_file.read()
        else:
            response_text = response.read()
        return response_text

class Amazon(AmazonCall):
    def __init__(self, AWSAccessKeyId=None, AWSSecretAccessKey=None, \
            AssociateTag=None, Operation=None, Version="2010-11-01", Region="US"):
        AmazonCall.__init__(self, AWSAccessKeyId, AWSSecretAccessKey, \
            AssociateTag, Operation, Version=Version, Region=Region)

__all__ = ["Amazon", "AmazonError"]

