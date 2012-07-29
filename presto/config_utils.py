import simplejson as json
from oauthlib.oauth1.rfc5849 import *
import httplib2
import urlparse
import urllib


class PrestoCfgException(Exception):
    pass

class PrestoCfg(object):

    def __init__(self):
        cfg_file = open('.presto', 'rw+')
        cfg = cfg_file.read()
        cfg_file.close()
        self.cfg = {}
        if cfg:
            self.cfg = json.loads(cfg)

    def save(self):
        if self.cfg:
            cfg_file = open('.presto', 'w')
            cfg_json = json.dumps(self.cfg, sort_keys=True, indent=4 * ' ')
            cfg_json = '\n'.join([l.rstrip() for l in  cfg_json.splitlines()])
            cfg_file.write(cfg_json)
            cfg_file.close()

    def provider_list(self):
        if self.cfg.get('providers', []):
            for i, provider in enumerate(self.cfg['providers']):
                print "[%d] %s" % (i+1, provider["name"])
            print ""
        else:
            raise PrestoCfgException("Please add provider.")

    def validate_provider_name(self, name):
        if self.cfg.get('providers', []):
            for provider in self.cfg['providers']:
                if provider['name'] == name:
                    raise PrestoCfgException("Provider with name '%s' already exist on provider '%s'." % \
                           (name, provider['name']))

    def validate_auth_type(self, type):
        if not type in (u'OAuth1.0', u'OAuth2.0'):
            raise PrestoCfgException("Invalid Auth type. Choose in ('OAuth1.0', 'OAuth2.0').")

    def validate_method(self, method):
        if not method in (u'POST', u'GET'):
            raise PrestoCfgException("Invalid method. Choose in ('POST', 'GET').")


    def provider_add(self, name=None, domain_name=None, auth_type=None, \
                    request_token_url=None, request_token_method=None, \
                    access_token_url=None, access_token_method=None, \
                    auth_url=None
                    ):
        if not name:
            print "Enter the name of the provider (e.g. 'odesk'):"
            name = unicode(raw_input())
            self.validate_provider_name(name)

        if not domain_name:
            print "Enter the domain name (may be comma-separated list):"
            domain_name = unicode(raw_input())

        if not auth_type:
            print "Enter the auth type ('OAuth1.0', 'OAuth2.0'):"
            auth_type = unicode(raw_input())
            self.validate_auth_type(auth_type)

        if not request_token_url:
            print "Request token URL:"
            request_token_url = unicode(raw_input())

        if not request_token_method: 
            print "Request token method ['POST']:"
            request_token_method = unicode(raw_input())
            if request_token_method == "":
                request_token_method = u'POST'
            self.validate_method(request_token_method)

        if not access_token_url:
            print "Access token URL:"
            access_token_url = unicode(raw_input())

        if not access_token_method:
            print "Access token method ['POST']:"
            access_token_method = unicode(raw_input())
            if access_token_method == "":
                access_token_method = u'POST'
            self.validate_method(access_token_method)

        if not auth_url:
            print "Auth URL:"
            auth_url = unicode(raw_input())

        provider = {
            "name": name,
            "domain_name": domain_name,
            "auth_type": auth_type,
            "request_token_url": request_token_url,
            "request_token_method": request_token_method,
            "access_token_url": access_token_url,
            "access_token_method": access_token_method,
            "auth_url": auth_url
        }

        if not self.cfg.has_key('providers'):
           self.cfg['providers'] = []
        self.cfg['providers'].append(provider)

        self.save()

        print "Added new provider %s" % (name)

    def app_list(self):
        apps_count = 0
        if self.cfg.get('providers', []):
            for i, provider in enumerate(self.cfg['providers']):
                if provider.get('apps', []):
                    for app in provider['apps']:
                        apps_count+=1
                        print "[%d] %s (%s)" % \
                        (apps_count, app["name"], provider['name'])
            print ""
        else:
            raise PrestoCfgException("Please add provider.")

    def get_provider_by_id(self, provider):
        try:
            provider = int(provider)
        except Exception:
            raise PrestoCfgException("Provider argument must be integer.")

        providers = self.cfg.get("providers", None)

        if not providers:
            raise PrestoCfgException("Please add provider.")

        if provider <= len(providers) and provider > 0:
            provider = providers[provider - 1]
        else:
            raise PrestoCfgException("Provider must be from 1 to %d." % len(providers))
        return provider

    def get_provider_by_name(self, name):

        providers = self.cfg.get("providers", None)

        if not providers:
            raise PrestoCfgException("Please add provider.")

        for provider in providers:
            if provider['name'] == name:
                return provider
        raise PrestoCfgException("Provider with name %s does not found." % name)

    def get_provider_by_domain_name(self, domain_name):

        providers = self.cfg.get("providers", None)

        if not providers:
            raise PrestoCfgException("Please add provider.")

        for provider in providers:
            if provider['domain_name'] == domain_name:
                return provider
        raise PrestoCfgException("Provider with domain name %s does not found." % domain_name)

    def get_app_by_name(self, provider, name):
        for app in provider['apps']:
            if app['name'] == name:
                return app
        raise PrestoCfgException("App with name '%s' does not found for provider '%s'.\nAvaliable:\n%s" % \
        (name, provider['name'], "\n".join([i['name'] for i in provider['apps']])))

    def app_check(self, provider, name):
        for app in provider['apps']:
            if app['name'] == name:
                raise PrestoCfgException("App with name '%s' already exist on provider '%s'." % \
                       (name, provider['name']))

    def app_add(self, provider, public_key, secret_key, name='default'):

        provider = self.get_provider_by_id(provider)
        self.app_check(provider, name)

        if not provider.has_key('apps'):
           provider['apps'] = []
        provider['apps'].append({ "name": name,
                                "public_key": public_key,
                                "secret_key": secret_key })
        self.save()


    def get_request_token(self):
        """
        Returns request token and request token secret
        """
        request_token_url = unicode(self.provider['request_token_url'])
        request_token_method = unicode(self.provider['request_token_method'])
        c = Client(unicode(self.app['public_key']),
            unicode(self.app['secret_key']), signature_type=SIGNATURE_TYPE_QUERY
        )
        uri, headers, body =  c.sign(uri=request_token_url, http_method=request_token_method)
        http = httplib2.Http()

        response, content = httplib2.Http.request(http, uri, method=request_token_method, body=body,
            headers=headers)

        if response.get('status') != '200':
            raise Exception("Invalid request token response: %s." % content)
        request_token = dict(urlparse.parse_qsl(content))
        self.request_token = unicode(request_token.get('oauth_token'))
        self.request_token_secret = unicode(request_token.get('oauth_token_secret'))
        return self.request_token, self.request_token_secret

    def get_authorize_url(self, callback_url=None):
        """
        Returns authentication URL to be used in a browser
        """
        auth_url = unicode(self.provider['auth_url'])
        oauth_token = getattr(self, 'request_token', None) or\
            self.get_request_token()[0]
        if callback_url:
            params = urllib.urlencode({'oauth_token': oauth_token,\
                'oauth_callback': callback_url})
        else:
            params = urllib.urlencode({'oauth_token': oauth_token})
        return '%s?%s' % (auth_url, params)

    def get_access_token(self, verifier):
        """
        Returns access token and access token secret
        """
        try:
            request_token = self.request_token
            request_token_secret = self.request_token_secret
        except AttributeError, e:
            raise Exception("At first you need to call get_authorize_url")
        access_token_url = unicode(self.provider['access_token_url'])
        access_token_method = unicode(self.provider['access_token_method'])

        c = Client(unicode(self.app['public_key']),
            unicode(self.app['secret_key']),
            resource_owner_key=request_token,
            resource_owner_secret=request_token_secret,
            signature_type=SIGNATURE_TYPE_QUERY,
            verifier=verifier
        )

        uri, headers, body =  c.sign(uri=access_token_url, http_method=access_token_method)
        http = httplib2.Http()

        response, content = httplib2.Http.request(http, uri, method=access_token_method, body=body,
            headers=headers)

        if response.get('status') != '200':
            raise Exception("Invalid access token response: %s." % content)
        access_token = dict(urlparse.parse_qsl(content))
        self.access_token = access_token.get('oauth_token')
        self.access_token_secret = access_token.get('oauth_token_secret')
        return self.access_token, self.access_token_secret

    def get_token_by_name(self, app, name):
        for token in app['tokens']:
            if token['name'] == name:
                return token
        raise PrestoCfgException("Token with name %s does not found." % name)
        
    def token_check(self, app, name):
        for token in app['tokens']:
            if token['name'] == name:
                raise PrestoCfgException("Token with name '%s' already exist on app '%s'." % \
                       (name, app['name']))

    def token_add(self, provider, app, name):
       if not name:
          name = 'default'
       self.provider = self.get_provider_by_id(provider)
       self.app = self.get_app_by_name(self.provider, app)
       self.token_check(self.app, name)
       self.get_request_token()

       print "Paste this URL to your browser: '%s'" % (self.get_authorize_url())
       print "Enter 'oauth_access_token' that you got:"

       verifier = unicode(raw_input())
       self.get_access_token(verifier)
       token = {'name': name,
                'token_key': self.access_token,
                'token_secret':self.access_token_secret}
       if not self.app.has_key('tokens'):
           self.app['tokens'] = []
       self.app['tokens'].append(token)
       self.save()

       print "The token is saved as '%s'." % (name)
