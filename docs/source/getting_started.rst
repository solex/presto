===============
Getting started
===============


The basic concepts
==================

**Provider**: Service provider (e.g. odesk.com, twitter.com)

**App**: Essentially, the set of keys. You can have multiple apps per provider.

**Token**: Access token. You can have multiple tokens per app.


.. _install:

Installation
============

On most UNIX-like systems, you probably need to run these commands as root or using sudo.

To install::

    python setup.py install

Or via easy_install::

    easy_install presto

Or via pip::

    pip install presto

Also, you can retrieve fresh version of pRESTo library from GitHub::

    git clone git://github.com/odesk/presto.git


Configuration
=============

First of all, you'll need to add provider::

    $ presto-cfg provider add
    >>> Enter the name of the provider (e.g. 'odesk'):
        ...
    >>> Enter the domain name:
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

Or using one of pre-configured providers::

   $ presto-cfg.py provider list
   >>> [1] odesk
   >>> [2] Twitter
   >>>  ...

You need to have at least one app. You can add it using `app add` command::

    $ presto-cfg app add
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
`presto-url`::

    $ presto-cfg token add
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

Using
=====

Example::

   $ presto-url -ac https://www.odesk.com/api/hr/v2/userroles.json
   >>> {
   >>> "auth_user": {
   >>>     "first_name": "Nikolay",
   >>>     "last_name": "Melnik",
   >>>     "uid": "nmelnik",
   >>>     "timezone_offset": "10800",
   >>>     "timezone": "EET",
   >>>     "mail": "nmelnik@odesk.com"
   >>> },
   >>> "server_time": "1345813337",
   >>> "user": {
   >>> ...