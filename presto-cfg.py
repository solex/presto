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
    >>> Choose the provider:
        [1] odesk
        [2] twitter
        ...
    >>> Enter the name of the app ['default']:
        ...
    >>> Enter the public key:
        ...
    >>> Enter the secret key:
        ...
    Added new app ...

Here's how you add new authorization (access token), that can be then used by
`presto-url`:

    presto-cfg token add
    >>> Choose the provider:
        [1] odesk
        [2] twitter
        ...
    >>> Choose the app:
        [1] *default*
        [2] newapp
    >>> Enter the name of the authorization ['default']
        ...
    >>> Using 'OAuth1.0'
    >>> Paste this URL to your browser: '...'
    >>> Enter 'oauth_verifier' that you got:
        ...
    >>> The token is saved as '...'


Many parameters can be supplied non-interactively by using options, e.g.:

    presto-cfg token add default --provider=odesk --app=default

Usage: presto-cfg.py provider list
       presto-cfg.py provider add [<name>]
       presto-cfg.py app list
       presto-cfg.py app add [<name> ] [--provider=<provider>|--public_key=<public_key>|--secret_key=<secret_key>]
       presto-cfg.py token add [<name>] [--provider=<provider>|--app=<app>]
       presto-cfg.py -h | --help
       presto-cfg.py --version

Options:

    --provider=<provider> Name of the auth provider
    --app=<app> Name of the app
    --public_key=<public_key>
    --secret_key=<secret_key>

"""

import sys
from docopt import docopt
from presto.config_utils import PrestoCfg, PrestoCfgException
from presto import version

ver = version.get_version()

if __name__ == '__main__':
    args = docopt(__doc__, argv=sys.argv[1:], help=True, version=ver)

    prestocfg = PrestoCfg()

    try:
        if args['provider'] and args['list']:
            prestocfg.provider_list()

        elif args['provider'] and args['add']:
            prestocfg.provider_add(args['<name>'])

        elif args['app'] and args['list']:
            prestocfg.app_list()

        elif args['app'] and args['add']:
            prestocfg.app_add(args['--provider'], args['--public_key'], args['--secret_key'], args['<name>'])

        elif args['token'] and args['add']:
            prestocfg.token_add(args['--provider'], args['--app'], args['<name>'])

    except PrestoCfgException, e:
         print "Error: %s " % e
