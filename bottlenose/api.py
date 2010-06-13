from base64 import b64encode
from hashlib import sha256
import urllib
import hmac
import time

from exceptions import Exception

class AmazonError(Exception):
    pass

class AmazonCall(object):
    def __init__(self, AWSAccessKeyId = None, AWSSecretAccessKey = None, \
            AssociateTag = None, Operation = None, Version = "2009-10-01"):
        self.AWSAccessKeyId = AWSAccessKeyId
        self.AWSSecretAccessKey = AWSSecretAccessKey
        self.Operation = Operation
        self.AssociateTag = AssociateTag
        self.Version = Version

    def signed_request(self):
        pass

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except:
            return AmazonCall(self.AWSAccessKeyId, self.AWSSecretAccessKey, \
                    self.AssociateTag, Operation = k)

    def __call__(self, **kwargs):
        kwargs['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        kwargs['Operation'] = self.Operation
        kwargs['Version'] = self.Version
        kwargs['AWSAccessKeyId'] = self.AWSAccessKeyId
        kwargs['Service'] = "AWSECommerceService"

        if self.AssociateTag:
            kwargs['AssociateTag'] = self.AssociateTag

        if 'Style' in kwargs:
            service_domain = "xml-us.amznxslt.com"
        else:
            service_domain = "ecs.amazonaws.com"

        keys = kwargs.keys()
        keys.sort()

        quoted_strings = "&".join("%s=%s" % (k, urllib.quote(str(kwargs[k]).encode('utf-8'), safe = '~')) for k in keys)

        data = "GET\n" + service_domain + "\n/onca/xml\n" + quoted_strings

        digest = hmac.new(self.AWSSecretAccessKey, data, sha256).digest()
        signature = urllib.quote(b64encode(digest))

        response = urllib.urlopen("http://" + service_domain + "/onca/xml?" + quoted_strings + "&Signature=%s" % signature)
        return response.read()

class Amazon(AmazonCall):
    def __init__(self, AWSAccessKeyId = None, AWSSecretAccessKey = None, \
            AssociateTag = None, Operation = None, Version = "2009-10-01"):
        AmazonCall.__init__(self, AWSAccessKeyId, AWSSecretAccessKey, \
            AssociateTag, Operation, Version = "2009-10-01")

__all__ = ["Amazon", "AmazonError"]

