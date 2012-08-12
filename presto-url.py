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
from  json_tools.printer import print_json


from presto.config_utils import PrestoCfg, PrestoCfgException
from presto import version
from presto.models import config

ver = version.get_version()

if __name__ == '__main__':
    args = docopt(__doc__, argv=sys.argv[1:], help=True, version=ver)
    url = unicode(args['<url>'])
    sch, net, path, par, query, fra = urlparse(url)

    method = unicode((args['--request'] or u'GET').upper())
    data = args['-d']

    try:
        if args['-a']:
            if args['--auth-provider']:
                provider = config.filter("providers", name=args['--auth-provider'])
            else:
                provider = config.filter("providers", domain_name=net)

            app_name = args['--auth-app'] or u'default'
            app = provider.filter('apps', name=app_name)

            token_name = args['--auth-token'] or u'default'
            token =  app.filter('tokens', name=token_name)

            access_token_key = token.token_key
            access_token_secret = token.token_secret
    except PrestoCfgException, e:
         print "Error: %s " % e
         raise

    client = Client(
        app.public_key,
        app.secret_key,
        resource_owner_key=access_token_key,
        resource_owner_secret=access_token_secret,
        signature_type=SIGNATURE_TYPE_QUERY
    )
    headers = {}
    if data:
        headers['Content-Type'] = u'application/x-www-form-urlencoded'
    uri, headers, body =  client.sign(uri=url, http_method=method, headers=headers, body=data)
    http = httplib2.Http()
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
    if response["content-type"] == "application/json":
        if args['-c']:
            print_json(json.loads(content), True)
        elif args['-p']:
            print_json(json.loads(content), False)
        else:
            print content
    else:
        print content
