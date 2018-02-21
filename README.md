<!--
Copyright 2012-2017 Lionheart Software LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

![](meta/repo-banner-2.png)

[![Version](https://img.shields.io/travis/lionheart/bottlenose.svg?style=flat)](https://travis-ci.org/lionheart/bottlenose)
[![Version](https://img.shields.io/pypi/v/bottlenose.svg?style=flat)](https://pypi.python.org/pypi/bottlenose)
[![License](https://img.shields.io/pypi/l/bottlenose.svg?style=flat)](LICENSE)
[![Versions](https://img.shields.io/pypi/pyversions/bottlenose.svg?style=flat)](https://pypi.python.org/pypi/bottlenose)

Bottlenose is a thin, well-tested, maintained, and powerful Python wrapper over the Amazon Product Advertising API.  There is practically no overhead, and no magic (unless you add it yourself).

Before you get started, make sure you have both Amazon Product Advertising and AWS accounts. `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_ASSOCIATE_TAG` are all from your Amazon Associate Account.

## Features

* [x] Compatible with Python versions 2.4 and up
* [x] Support for BR, CA, CN, DE, ES, FR, IN, IT, JP, MX, UK, and US Amazon Product Advertising API endpoints
* [x] No requirements, except simplejson for Python versions before 2.6
* [x] Configurable query parsing
* [x] Configurable throttling for batches of queries
* [x] Configurable query caching
* [x] Configurable error handling and retries

## Usage

### [pip](https://pip.pypa.io/en/stable/installing/)

    pip install bottlenose

or

    python3 -m pip install bottlenose

Then, using your `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_ASSOCIATE_TAG`:

```python
import bottlenose
amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
response = amazon.ItemLookup(ItemId="B007OZNUCE")
```

You can then parse the `response` output to view item information.

## Troubleshooting

* If you need help or would like to ask a general question, use [Stack Overflow](http://stackoverflow.com/questions/tagged/bottlenose). Apply the 'bottlenose' tag to your question to get help faster.
* If you found a bug or have a feature request, open an issue.
* If you want to contribute, submit a pull request. If it's a big change, please open an issue first to discuss implementation.

## Advanced Usage

#### 1. Available Search Methods

##### Region Endpoint

The default Region is the US (`webservices.amazon.com`). To specify a different endpoint
simply set the Region parameter with the request. For example to specify the French
endpoint (`webservices.amazon.fr`) set the Region parameter to 'FR':

```python
amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG, Region='FR')
```
Supported values for the Region parameter are CA, CN, DE, ES, FR, IN, IT, JP, UK, and US (default).

Your Amazon Product Advertising account (AWS_ASSOCIATE_TAG) mut exist for the given endpoint
or you'll get an HTTP 400 error ('Bad Request').

##### Search for a Specific Item

```python
response = amazon.ItemLookup(ItemId="B007OZNUCE")
```

##### Search for Items by Keywords

```python
response = amazon.ItemSearch(Keywords="Kindle 3G", SearchIndex="All")
```

##### Search for Images for an item

```python
response = amazon.ItemLookup(ItemId="1449372422", ResponseGroup="Images")
```

##### Search for Similar Items

```python
response = amazon.SimilarityLookup(ItemId="B007OZNUCE")
```

#### 2. Available Shopping Related Methods

##### Required

```python
amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
```

##### Create a cart

```python
response = amazon.CartCreate(...)
```

##### Adding to a cart

```python
response = amazon.CartAdd(CartId, ...)
```

##### Get a cart by ID

```python
response = amazon.CartGet(CartId, ...)
```

##### Modifying a cart

```python
response = amazon.CartModify(ASIN, CartId,...)
```

##### Clearing a cart

```python
response = amazon.CartClear(CartId, ...)
```

#### 3. Sample Code

```python
import bottlenose
amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)
response = amazon.ItemLookup(ItemId="0596520999", ResponseGroup="Images",
    SearchIndex="Books", IdType="ISBN")
print(response)
# <?xml version="1.0" ?><ItemLookupResponse xmlns="http://webservices.amazon...
```

Here is another example.

```python
response = amazon.ItemSearch(Keywords="Kindle 3G", SearchIndex="All")
# <?xml version="1.0" ?><ItemSearchResponse xmlns="http://webservices.amazon...
```

Bottlenose can also read your credentials from the environment automatically;
just set `$AWS_ACCESS_KEY_ID`, `$AWS_SECRET_ACCESS_KEY` and
`$AWS_ASSOCIATE_TAG`.

Any valid API call from the following is supported (in addition to any others
that may be added in the future). Just plug in appropriate request parameters
for the operation you'd like to call, and you're good to go.

    BrowseNodeLookup
    CartAdd
    CartClear
    CartCreate
    CartGet
    CartModify
    ItemLookup
    ItemSearch
    SimilarityLookup

You can refer here for a full listing of API calls to be made from Amazon.
- [Amazon API Quick Reference Card](http://s3.amazonaws.com/awsdocs/Associates/latest/prod-adv-api-qrc.pdf)

-------

For more information about these calls, please consult the [Product Advertising
API Developer Guide](http://docs.aws.amazon.com/AWSECommerceService/latest/DG/Welcome.html).

## Parsing

By default, API calls return the response as a raw bytestring. You can change
this with the `Parser` constructor argument. The parser is a callable that
takes a single argument, the response as a raw bytestring, and returns the
parsed response in a format of your choice.

For example, to parse responses with BeautifulSoup:

```python
import bottlenose
from bs4 import BeautifulSoup

amazon = bottlenose.Amazon(
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG,
    Parser=lambda text: BeautifulSoup(text, 'xml')
)
results = amazon.ItemLookup(ItemId="0198596790", ResponseGroup="SalesRank")

print(results.find('SalesRank').string)
# 168088
```

## Throttling/Batch Mode

Amazon strictly limits the query rate on its API (by default, one query
per second per associate tag). If you have a batch of non-urgent queries, you
can use the `MaxQPS` argument to limit them to no more than a certain rate;
any faster, and bottlenose will `sleep()` until it is time to make the next
API call.

Generally, you want to be just under the query limit, for example:

```python
amazon = bottlenose.Amazon(MaxQPS=0.9)
```

If some other code is also querying the API with your associate tag (for
example, a website backend), you'll want to choose an even lower value
for MaxQPS.

## Caching

You can often get a major speedup by caching API queries. Use the `CacheWriter`
and `CacheReader` constructor arguments.

`CacheWriter` is a callable that takes two arguments, a cache url, and the
raw response (a bytestring). It will only be called after successful queries.

`CacheReader` is a callable that takes a single argument, a cache url, and
returns a (cached) raw response, or `None` if there is nothing cached.

The cache url is the actual query URL with authentication information removed.
For example:

    http://webservices.amazon.com/onca/xml?Keywords=vacuums&Operation=ItemSearch&Region=US&ResponseGroup=SearchBins&SearchIndex=All&Service=AWSECommerceService&Version=2013-08-01

Example code:

```python
def write_query_to_db(cache_url, data):
    ...

def read_query_from_db(cache_url):
    ...

amazon = bottlenose.Amazon(CacheWriter=write_query_to_db,
                           CacheReader=read_query_from_db)
```

Note that Amazon's [Product Advertising API Agreement](https://affiliate-program.amazon.com/gp/advertising/api/detail/agreement.html)
only allows you to cache queries for up to 24 hours.

## Error Handling

Sometimes the Amazon API returns errors; for example, if you have gone over
your query limit, you'll get a 503. The `ErrorHandler` constructor argument
gives you a way to keep track of such errors, and to retry queries when you
receive a transient error.

`ErrorHandler` should be a callable that takes a single argument, a dictionary
with these keys:

 * api_url: the actual URL used to call the API
 * cache_url: `api_url` minus authentication information
 * exception: the exception raised (usually an `HTTPError` or `URLError`)

If your `ErrorHandler` returns true, the query will be retried. Here's some
example code that does exponential backoff after throttling:

```python
import random
import time
from urllib2 import HTTPError

def error_handler(err):
    ex = err['exception']
    if isinstance(ex, HTTPError) and ex.code == 503:
        time.sleep(random.expovariate(0.1))
        return True

amazon = bottlenose.Amazon(ErrorHandler=error_handler)
```

## License

Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
