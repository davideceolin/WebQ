import requests


def call(url):
    key = "d013ef2a8b3c5567ca0c5f73dcbef999c510da93"
    url_base = 'http://gateway-a.watsonplatform.net/calls/url/URLGetCombinedData?extract=entity,keyword,title,author,taxonomy,concept,relation,pub-date,doc-sentiment,doc-emotion&apikey='+key+'&sentiment=1&quotations=1&outputMode=json&url='+url
    return requests.get(url_base).json()




