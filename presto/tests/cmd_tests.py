#!/usr/bin/env python
# coding: utf-8

import os, sys, json, functools, random
import StringIO
from mock import patch
from unittest import TestCase
from presto.config_utils import PrestoCfg
from presto.models import Configuration
from presto.models import config
from presto.utils.exceptions import ValidationError


TEST_CONFIG_NAME = os.path.join(os.path.dirname(__file__), 'test_presto.cfg')


def intercept_output(func, *args, **kwargs):
    '''
    Decorator, that intercepts command output and returns it as second ret value.

    :param func: function to decorate.
    '''
    @functools.wraps(func)
    def _func(*args, **kwargs):
        result = None
        output = ''
        saved_stdout = sys.stdout
        try:
            out = StringIO.StringIO()
            sys.stdout = out
            result = func(*args, **kwargs)
            output = out.getvalue().strip()
        finally:
            sys.stdout = saved_stdout
        return result, output
    return _func

def get_access_token_mock(self, *args, **kwargs):
    return 'access_token', 'access_token_secret'

def build_authorize_url_mock(self, *args, **kwargs):
    return "www.auth.com"

def get_request_token_mock(self, *args, **kwargs):
    return 'request_token', 'request_token_secret'


class TestConfigCommands(TestCase):
    """
    Tests for creating presto configuration commands.
    """
    def setUp(self):
        test_config = Configuration()
        test_config.load_from_file(TEST_CONFIG_NAME)
        self.prestocfg = PrestoCfg(conf=test_config)

    def test_provider_list(self):
        """
        Tests `provider_list` command.
        """
        @intercept_output
        def provider_list():
            return self.prestocfg.provider_list()

        result, output = provider_list()
        self.assertEqual(result, None,
                         'Nothing should be returned')
        provider_count = 0
        for provider in self.prestocfg.config.providers:
            self.assertTrue(provider.name in output,
                            'Provider %s not found' % provider.name)
            provider_count += 1
        self.assertEqual(provider_count, 2)

    @patch('presto.models.Configuration.save_to_file')
    def test_add_provider(self, *mocks):
        """
        Tests `provider_add` command.
        """
        @intercept_output
        def provider_add(name, domain_name, auth_type,
                    request_token_url, request_token_method,
                    access_token_url, access_token_method,
                    auth_url):
            return self.prestocfg.provider_add(name, domain_name, auth_type,
                    request_token_url, request_token_method,
                    access_token_url, access_token_method,
                    auth_url)

        kwargs = dict(name='Test Provider',
                      domain_name='test.com',
                      auth_type='OAuth1.0',
                      request_token_url='www.token.com/request',
                      request_token_method='POST',
                      access_token_url='www.token.com/access',
                      access_token_method='POST',
                      auth_url='www.test.com/auth')
        result, output = provider_add(**kwargs)
        self.assertEqual(result, None,
                         'Nothing should be returned')
        name = kwargs['name']
        self.assertTrue("Added new provider '%s'" % (name) in output, output)

    def test_app_list(self):
        """
        Tests `app_list` command.
        """
        @intercept_output
        def app_list():
            return self.prestocfg.app_list()

        result, output = app_list()
        self.assertEqual(result, None,
                         'Nothing should be returned')
        apps_count = 0
        for provider in self.prestocfg.config.providers:
            for app in provider.apps:
                self.assertTrue(app.name in output,
                            'App %s not found' % app.name)
                apps_count += 1
        self.assertEqual(apps_count, 3)

    @patch('presto.models.Configuration.save_to_file')
    def test_app_add(self, *mocks):
        """
        Tests `app_add` command.
        """
        @intercept_output
        def app_add(provider, public_key, secret_key, name):
            return self.prestocfg.app_add(provider, public_key, secret_key, name)

        kwargs = dict(provider="1", 
                      public_key="public key", 
                      secret_key="private key", 
                      name='app1')
        result, output = app_add(**kwargs)
        self.assertEqual(result, None,
                         'Nothing should be returned')
        name = kwargs['name']
        self.assertTrue("Added new app '%s'" % (name) in output, output)

    @patch("presto.oauth.get_request_token", get_request_token_mock)
    @patch("presto.oauth.build_authorize_url", build_authorize_url_mock)
    @patch("presto.oauth.get_access_token", get_access_token_mock)
    @patch('presto.utils.utils.input')
    def test_token_add(self, input_mock, *mocks):
        """
        Tests `token_add` command.
        """
        input_mock.return_value = 'OK'

        @intercept_output
        def token_add(provider, app, name):
            return self.prestocfg.token_add(provider, app, name)

        kwargs = dict(provider='1', 
                      app='1', 
                      name='token')
        result, output = token_add(**kwargs)
        self.assertEqual(result, None,
                         'Nothing should be returned')

        self.assertTrue("The token is saved as '%s'" % kwargs['name'] \
                                                    in output, output)
