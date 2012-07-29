#!/usr/bin/env python
# coding: utf-8

"""pRESTo


The program uses `curl` conventions when appropriate, but compatibility with
`curl` is not a priority.

Usage: presto-url.py [options] <url>
       presto-url.py -h | --help
       presto-url.py --version

Options:

  -a  Use authentication. It will use the default auth method and security
      credentials for a domain name in a given URL. Provider, app and other
      params can be set explicitly. See the documentation for `presto-cfg`
  --auth-app=<auth-app>  Name of the app to use for authentication. See the
            documentation for `presto-cfg`
  --auth-token=<auth-token>    Name of the auth token.
  --auth-provider=<auth-provider>  Name of the auth provider
  -c  Colorize output.
  -p  Pretty-print the output.
  -d <data>  Data to send.
  -i  Include HTTP headers in the output.
  -I  Display headers only. Please note that this does *not* use HTTP HEAD
      method. Use -X instead if you need it.
  -H | --header <header> Extra HTTP header to use.
  -X | --request <method> Specify a custom HTTP request method.

Example:

  presto-url.py -icpa -X post http://www.odesk.com/api/

"""

import sys
from docopt import docopt
from oauthlib.oauth1.rfc5849 import *
from urlparse import urlparse
import httplib2
import simplejson as json


from presto.config_utils import PrestoCfg, PrestoCfgException
from  json_tools.printer import print_json

version = __import__('presto').get_version()

if __name__ == '__main__':
    args = docopt(__doc__, argv=sys.argv[1:], help=True, version=version)
    #print(args)
    url = unicode(args['<url>'])
    sch, net, path, par, query, fra = urlparse(url)
    
    method = args['--request'] or u'GET'
    prestocfg = PrestoCfg()
    try:
        if args['-a']:
            if args['--auth-provider']:
                provider = prestocfg.get_provider_by_name(args['--auth-provider'])
            else:
                provider = prestocfg.get_provider_by_domain_name(net)

            app_name = args['--auth-app'] or u'default'
            app = prestocfg.get_app_by_name(provider, app_name)

            token_name = args['--auth-token'] or u'default'
            token =  prestocfg.get_token_by_name(app, token_name)
            access_token_key = unicode(token['token_key'])
            access_token_secret = unicode(token['token_secret'])
    except PrestoCfgException, e:
         print "Error: %s " % e
         raise

    client = Client(unicode(app['public_key']),
            unicode(app['secret_key']),
            resource_owner_key=access_token_key,
            resource_owner_secret=access_token_secret,
            signature_type=SIGNATURE_TYPE_QUERY
    )
    uri, headers, body =  client.sign(uri=url, http_method=method)
    http = httplib2.Http()
    headers['Content-Type'] = u'application/x-www-form-urlencoded'
    response, content = httplib2.Http.request(http, uri, method=method, body=body,
            headers=headers)

    if args['-i']:
        print "\nHeaders:"
        if args['-c']:
            print_json(dict(headers), True)
        elif args['-p']:
            print_json(dict(headers), False)
        else:
            print headers

    print "\nResponse:"
    if args['-c']:
        print_json(dict(response), True)
    elif args['-p']:
        print_json(dict(response), False)
    else:
        print response

    print "\nContent:"
    if args['-c']:
        print_json(json.loads(content), True)
    elif args['-p']:
        print_json(json.loads(content), False)
    else:
        print content