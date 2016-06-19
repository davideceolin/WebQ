""" Module for acting as a proxy for fetching contents of a url """
import urllib2
import json
import urlparse
import re
import cchardet

def _validateUrl(urlstr):
    pattern = re.compile(
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    protocol = re.match(r'^(\w+)://',urlstr)

    # if a protocol is specified make sure its only http or https
    if (protocol != None) and not(bool(re.match(r'(?:http)s?',protocol.groups()[0]))):
        return False

    return bool(re.search(pattern,urlstr))

def get(qstring):
    """ Builds and returns a JSON reply of all information and requested data """
    args = dict(urlparse.parse_qsl(qstring)) 
 
    reply = {}
    reply["headers"] = {}
    reply["status"] = {}

    if "url" in args and _validateUrl(args["url"]):
        reply["status"]["url"] = args["url"]
        
        if not args["url"].startswith("http://") and not args["url"].startswith("https://") :
            args["url"] = "http://"+args["url"] 
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
        req = urllib2.Request(args["url"],headers=hdr)
    
        try: 
            response = urllib2.urlopen(req)
            charset = response.headers.getparam('charset')
            if charset is not None:
                resp = response.read()
                try:
                    reply["content"] = resp.decode(charset)
                except:
                    try:
                        reply["content"] = resp.decode(cchardet.detect(resp)['encoding'])
                    except:
                        reply["content"] = resp
            else:
                resp = response.read()
                try:
                    reply["content"] = resp.decode(cchardet.detect(resp)['encoding'])
                except:
                    reply["content"] = resp
            reply["status"]["http_code"] = response.code

            if "headers" in args and args["headers"] == "true":
                reply["headers"] = dict(response.info())

        except (urllib2.HTTPError, urllib2.URLError) as e:
            try:
                reply['content'] = urllib2.build_opener(urllib2.HTTPCookieProcessor).open(args["url"]).read()
            except:
                reply["status"]["reason"] = str(e.reason)
                reply["content"] = None
                reply["status"]["http_code"] = e.code if hasattr(e,'code') else 0
    else:
        reply["content"] = None
        reply["status"]["http_code"] = 400
        reply["status"]["reason"] = "The url parameter value is missing or invalid"
   
    # Attach callback to reply if jsonp request
    if "callback" in args:
        return "{0}({1})".format(args["callback"], json.dumps(reply))
    return json.dumps(reply, ensure_ascii=False)
