==========
Presto-cfg
==========

Usage::

    presto-cfg.py provider list
    presto-cfg.py provider add [<name>]
    presto-cfg.py app list
    presto-cfg.py app add [<name> ] [--provider=<provider>|--public_key=<public_key>|--secret_key=<secret_key>]
    presto-cfg.py token add [<name>] [--provider=<provider>|--app=<app>]
    presto-cfg.py token update [<name>] [--provider=<provider>|--app=<app>]
    presto-cfg.py -h | --help
    presto-cfg.py --version

Options:

  --provider=<provider>      Name of the auth provider.
  --app=<app>                Name of the app.
  --public_key=<public_key>  Public key.
  --secret_key=<secret_key>  Secret key.

Providers specific commands
===========================

`provider list` can be used to display providers list::

    $ python presto-cfg.py provider list
    >>> [1] odesk
    >>> [2] Twitter

`provider add` adds new provider to configuration file with specified fields:

 * name
    Unique name of the auth provider.
 * domain name
    Domain name, e.g. www.odesk.com.
 * auth_type
    System supports OAuth1.0 and OAuth2.0 authentication types.
    OAuth2.0 will be used by default.
 * request_token_url
 * request_method
 * access_token_url
 * access_token_method
 * auth_url


App specific commands
=====================

`app list` can be used to display apps list::

    $ python presto-cfg.py app list
    >>> [1] default (odesk)
    >>> [2] default (Twitter)
    >>> [3] other-app (Twitter)


`app add` adds new app to the provider configuration with fields:

 * name
    Unique for each provider app name.
 * public_key
 * secret_key


Token specific commands
=======================

`token add` requests and saves to configuration file access tokens.
If token with specified name already exist, system will ask another one name of the token.
Adds token record to configuration file with fields::

 * name
 * token_key
 * token_secret


`token update` requests and rewrites tokens to the configuration.
