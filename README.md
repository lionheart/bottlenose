Bottlenose
==========

Description
-----------

Bottlenose takes care of everything you might want to do with the Amazon
Product Advertising API.  Unlike other libraries, Bottlenose doesn't tell you
what you can and can't do. For example: let's say Amazon adds a new possible
value for their Operation parameter. No problem! Bottlenose lets you
incorporate these changes into your code immediately, even without updating
Bottlenose. How? Check it out below.

Usage
-----

Creation::

     >>> import bottlenose
     >>> amazon = bottlenose.Amazon(access_key_id, secret_access_key, associate_tag)
     >>> response = amazon.ItemLookup(ItemId = "0596520999", ResponseGroup =
         "Images", SearchIndex = "Books", IdType = "ISBN",
         Style="http://xml2json-xslt.googlecode.com/svn/trunk/xml2json.xslt")
     {"ItemLookupResponse":{"OperationRequest":{"HTTPHeaders":{"Header":null},"Re...

Notice that I do not like XML. Despite this, you are free to omit the `Style`
parameter when making your calls to Amazon. I like using an amazing XSLT
stylesheet written by Doeke Zanstra that does its best to convert XML to JSON.
As far as I can tell, it does a pretty amazing job with Amazon's responses.
I've included the stylesheet in this project if you'd like to host it yourself.

Want to grab some other data? No problem! Bottlenose to the rescue::

     >>> response = amazon.Help(About = "ListSearch", HelpType = "Operation")
     <?xml version="1.0" encoding="UTF-8"?><HelpResponse xmlns="http://webserv...

Any valid API call from the following is supported (in addition to any others
that may be added in the future--the code is self-healing, it's amazing!)::

     BrowseNodeLookup
     CartAdd
     CartClear
     CartCreate
     CartGet
     CartModify
     CustomerContentLookup
     CustomerContentSearch
     Help
     ItemLookup
     ItemSearch
     ListLookup
     ListSearch
     SellerListingLookup
     SellerListingSearch
     SellerLookup
     SimilarityLookup
     TagLookup
     TransactionLookup
     VehiclePartLookup
     VehiclePartSearch
     VehicleSearch

For more information about these calls, please consult the Product Advertising
API Developer Guide (http://docs.amazonwebservices.com/AWSECommerceService/latest/DG/index.html).

License
-------

Copyright &copy; 2010 Dan Loewenherz

See LICENSE for details.
