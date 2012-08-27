==========
Presto-url
==========

Usage::

    presto-url.py [options] <url>
    presto-url.py -h | --help
    presto-url.py --version


Options:

  -a  Use authentication. It will use the default auth method and security
      credentials for a domain name in a given URL. Provider, app and other
      params can be set explicitly. See the documentation for `presto-cfg`
  --auth-app=<auth-app>  Name of the app to use for authentication. See the
      documentation for `presto-cfg`
  --auth-token=<auth-token>  Name of the auth token.
  --auth-provider=<auth-provider>  Name of the auth provider
  -c  Colorize output.
  -p  Pretty-print the output.
  -d <data>  Data to send.
  -i  Include HTTP headers in the output.
  -I  Display headers only. Please note that this does *not* use HTTP HEAD
      method. Use -X instead if you need it.
  -H, --header <header>  Extra HTTP header to use.
  -X, --request <method>  Specify a custom HTTP request method.
