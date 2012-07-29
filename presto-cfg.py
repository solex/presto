#!/usr/bin/env python
# coding: utf-8

"""presto-cfg

Configuration utility for pRESTo


The basic concepts:
Provider: Service provider (e.g. odesk.com, twitter.com)
App: Essentially, the set of keys. You can have multiple apps per provider
Token: Access token. You can have multiple tokens per app.

When using auto-auth with presto-url, it figures the right provider from the
domain name.
The 'default' name for apps and auth tokens have special meaning. They will be
used by auto-auth if no explicit names are provided.

Presto stores all configuration files in '~/.presto/' as .json


Presto comes with several preconfigured domains. To list them:

    presto-cfg provider list
    >>> [1] odesk
    >>> [2] twitter
    >>> ...

To add the new one:

    presto-cfg provider add
    >>> Enter the name of the provider (e.g. 'odesk'):
        ...
    >>> Enter the domain name (may be comma-separated list):
        ...
    >>> Enter the auth type ('OAuth1.0', 'OAuth2.0'):
        ...
    >>> Request token URL:
        ...
    >>> Request token method ['POST']:
        ...
    >>> Access token URL:
        ...
    >>> Access token method ['POST']:
        ...
    >>> Auth URL:
        ...
    Added new provider ...

You need to have at least one app (set of keys) per each provider:

    presto-cfg app add
    >>> Enter the name of the app ['default']:
        ...
    >>> Choose the provider:
        [1] odesk
        [2] twitter
        ...
    >>> Enter the public key:
        ...
    >>> Enter the secret key:
        ...
    Added new app ...

Here's how you add new authorization (access token), that can be then used by
`presto-url`:

    presto-cfg token add
    >>> Enter the name of the authorization ['default']
        ...
    >>> Choose the provider:
        [1] odesk
        [2] twitter
        ...
    >>> Choose the app:
        [1] *default*
        [2] newapp
    >>> Using 'OAuth1.0'
    >>> Paste this URL to your browser: '...'
    >>> Enter 'oauth_access_token' that you got:
        ...
    >>> The token is saved as '...'


Many parameters can be supplied non-interactively by using options, e.g.:

    presto-cfg token add --name=default --provider=odesk --app=default

Usage: presto-cfg.py provider list
       presto-cfg.py provider add [<name>]
       presto-cfg.py app list
       presto-cfg.py app add <provider> <public_key> <secret_key> [<name> ]
       presto-cfg.py token add  <provider> <app> [<name>]
       presto-cfg.py -h | --help
       presto-cfg.py --version

Options:

    ...

"""

import sys
from docopt import docopt
from presto.config_utils import PrestoCfg, PrestoCfgException

version = __import__('presto').get_version()

if __name__ == '__main__':
    args = docopt(__doc__, argv=sys.argv[1:], help=True, version=version)

    prestocfg = PrestoCfg()

    try:
        if args['provider'] and args['list']:
            prestocfg.provider_list()

        elif args['provider'] and args['add']:
            prestocfg.provider_add(args['<name>'])

        elif args['app'] and args['list']:
            prestocfg.app_list(args['<name>'])

        elif args['app'] and args['add']:
            prestocfg.app_add(args['<provider>'], args['<public_key>'], args['<secret_key>'], args['<name>'])

        elif args['token'] and args['add']:
            prestocfg.token_add(args['<provider>'], args['<app>'], args['<name>'])

    except PrestoCfgException, e:
         print "Error: %s " % e
