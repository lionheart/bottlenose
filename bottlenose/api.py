from base64 import b64encode
from hashlib import sha256
import urllib
import urllib2
import hmac
import time

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
    def __init__(self, AWSAccessKeyId = None, AWSSecretAccessKey = None, \
            AssociateTag = None, Operation = None, Version = "2009-10-01", Region = "US"):
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
                    self.AssociateTag, Operation = k, Version = self.Version, Region = self.Region)

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

        quoted_strings = "&".join("%s=%s" % (k, urllib.quote(str(kwargs[k]).encode('utf-8'), safe = '~')) for k in keys)

        data = "GET\n" + service_domain + "\n/onca/xml\n" + quoted_strings

        digest = hmac.new(self.AWSSecretAccessKey, data, sha256).digest()
        signature = urllib.quote(b64encode(digest))

        api_string = "http://" + service_domain + "/onca/xml?" + quoted_strings + "&Signature=%s" % signature
        api_request = urllib2.Request(api_string)
        response = urllib2.urlopen(api_request)
        response_text = response.read()
        return response_text

class Amazon(AmazonCall):
    def __init__(self, AWSAccessKeyId = None, AWSSecretAccessKey = None, \
            AssociateTag = None, Operation = None, Version = "2009-10-01", Region = "US"):
        AmazonCall.__init__(self, AWSAccessKeyId, AWSSecretAccessKey, \
            AssociateTag, Operation, Version = Version, Region = Region)

__all__ = ["Amazon", "AmazonError"]

