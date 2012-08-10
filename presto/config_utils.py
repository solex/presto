#!/usr/bin/env python
# coding: utf-8

import os, functools
import simplejson as json
from oauthlib.oauth1.rfc5849 import *
import httplib2
import urlparse
import urllib

from presto.models import config, Provider, Application


def need_providers(func, *args, **kwargs):
    @functools.wraps(func)
    def _func(*args, **kwargs):
        if not config.providers:
            raise PrestoCfgException("Add providers please.")
        return func(*args, **kwargs)
    return _func


class PrestoCfgException(Exception):
    pass

class PrestoValidationError(PrestoCfgException):
    pass

class PrestoCfgAlreadyExist(PrestoCfgException):
    pass

class PrestoCfg(object):
    '''
    Commands for configuring presto utils.
    '''
    @need_providers
    def provider_list(self):
        '''
        Displays list of all providers in the config.
        '''
        for i, provider in enumerate(config.providers):
            print "[%d] %s" % (i + 1, provider.name)
        print ""

    @need_providers
    def app_list(self):
        '''
        Displays list of all applications in the config.
        '''
        apps_count = 0
        for i, prov in enumerate(config.providers):
            for app in prov.apps:
                apps_count += 1
                print "[%d] %s (%s)" % (apps_count, app.name, prov.name)
        print ""

    def provider_add(self, name=None, domain_name=None, auth_type=None,
                    request_token_url=None, request_token_method=None,
                    access_token_url=None, access_token_method=None,
                    auth_url=None
                    ):
        '''
        Adds new provider to the configuration.
        
        :param name: provider name.
        :param domain_name: provider domain.
        :param auth_type: provider auth type: OAuth1.0 or OAuth2.0.
        :param request_token_url:
        :param request_token_method:
        :param access_token_url:
        :param access_token_method:
        :param auth_url:
        '''
        provider = Provider(data=locals(), parent=config)
        if provider.is_valid():
            config.providers.append(provider)
        config.save_to_file()
        print "Added new provider '%s'" % (provider.name)

    @need_providers
    def app_add(self, provider, public_key, secret_key, name=None):
        '''
        Adds new application for specified `provider`.

        :param provider: provider positional index.
        :param public_key: application public key.
        :param secret_key: application secret key.
        :param name: application name.
        '''
        app = Application(data=locals(), parent=config)
        if app.is_valid():
            provider = app.cleaned_data['provider']
            provider.apps.append(app)
        config.save_to_file()
        print "Added new app '%s'" % app.name

    def app_list_by_provider(self, provider):
        for i, app in enumerate(provider['apps']):
            print "[%d] %s" % \
                (i+1, app["name"])

    def get_app_by_id(self, app, provider):
        try:
            app = int(app)
        except Exception:
            raise PrestoCfgException("App argument must be integer.")

        apps = provider.get("apps", None)

        if not apps:
            raise PrestoCfgException("Please add app.")

        if app <= len(apps) and app > 0:
            app = apps[app - 1]
        else:
            raise PrestoCfgException("Provider must be from 1 to %d." % len(apps))
        return app

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

    def validate_app_name(self, name, provider):
        for app in provider['apps']:
            if app['name'] == name:
                raise PrestoCfgAlreadyExist("App with name '%s' already exist on provider '%s'." % \
                       (name, provider['name']))

    def question(self, text, default=None, validation_func=None, ext_func=None, ext_param={}):
        while True:
            print text
            if ext_func:
                ext_func(**ext_param)
            value = unicode(self.input_func())
            if value == "" and default:
                value = default
            if value:
                if validation_func:
                    try:
                        val = validation_func(value, **ext_param)
                    except PrestoCfgAlreadyExist, e:
                        print e
                        while True:
                            print "Rewrite '%s'? (y/n)" % value
                            yes_no = unicode(self.input_func())
                            if yes_no in ('Y', 'y', 'yes', '\n'):
                                return value
                            if yes_no in ('N', 'n', 'no'):
                                raise e
                    except PrestoCfgException, e:
                        print e
                        continue
                    if val:
                        return val
                return value

    


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
            raise PrestoCfgException("At first you need to call get_authorize_url")
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
            raise PrestoCfgException("Invalid access token response: %s." % content)
        access_token = dict(urlparse.parse_qsl(content))
        self.access_token = access_token.get('oauth_token')
        self.access_token_secret = access_token.get('oauth_token_secret')
        return self.access_token, self.access_token_secret

    def get_token_by_name(self, app, name):
        for token in app['tokens']:
            if token['name'] == name:
                return token
        raise PrestoCfgException("Token with name %s does not found." % name)
        
    def validate_token_name(self, name, app):
        if app.get('tokens', None):
            for token in app['tokens']:
                if token['name'] == name:
                    raise PrestoCfgAlreadyExist("Token with name '%s' already exist on app '%s'." % \
                           (name, app['name']))

    def token_add(self, provider, app, name):

        if not provider:
            self.provider = self.question("Choose the provider:", \
                       ext_func=self.provider_list, \
                       validation_func = self.get_provider_by_id)
        else:
            self.provider = self.get_provider_by_name(provider)

        if not app:
            self.app = self.question("Choose the app:", \
                       ext_func=self.app_list_by_provider, \
                       ext_param={"provider": self.provider },
                       default = 'default',
                       validation_func = self.get_app_by_id)
        else:
            self.app = self.get_app_by_name(self.provider, app)

        if not name:
            name = self.question("Enter the name of the authorization ['default']:",\
                          "default", self.validate_token_name, \
                          ext_param={"app": self.app})

        self.get_request_token()

        print "Paste this URL to your browser: '%s'" % (self.get_authorize_url())

        self.question("Enter 'oauth_verifier' that you got:",
                    validation_func=self.get_access_token)
        token = {'name': name,
                'token_key': self.access_token,
                'token_secret':self.access_token_secret}

        if not self.app.has_key('tokens'):
            self.app['tokens'] = []
        token_ex_index = None
        for i, ex_token in enumerate(self.app['tokens']):
            if ex_token['name'] == name:
                token_ex_index = i
                break
        if token_ex_index != None:
            self.app['tokens'][token_ex_index] = token
        else:
            self.app['tokens'].append(token)

        self.save()

        print "The token is saved as '%s'." % (name)
