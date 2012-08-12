#!/usr/bin/env python
# coding: utf-8
from presto.models import config, Provider, Application, Token
from presto.utils.utils import need_providers
from presto.utils.exceptions import PrestoCfgException


class PrestoCfg(object):
    '''
    Commands for configuring presto utils.
    '''
    @need_providers
    def provider_list(self):
        '''
        Displays list of all providers in the config.
        '''
        config.provider_list()

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

    @need_providers
    def token_add(self, provider, app, name):
        '''
        
        :param provider:
        :param app:
        :param name:
        '''
        token = Token(data=locals(), parent=config)
        if token.is_valid():
            app = token.cleaned_data['app']
            app.tokens.append(token)

        config.save_to_file()
        print "The token is saved as '%s'." % (token.name)
