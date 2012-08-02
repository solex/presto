#!/usr/bin/env python
# coding: utf-8

import os, sys, json, functools, random
import StringIO
from mock import Mock, patch
from unittest import TestCase

from presto.config_utils import PrestoCfg, PrestoCfgException


TEST_CONFIG_NAME = os.path.join(os.path.dirname(__file__), 'test_presto.cfg')


def load_config(file_name):
        f = file(file_name, "r")
        cfg = f.read()
        f.close()
        return json.loads(cfg)


def intercept_output(view_func, *args, **kwargs):
    """
    Intercepts command output and returns it as second ret value.
    """
    @functools.wraps(view_func)
    def _view_func(*args, **kwargs):
        result = None
        output = ''
        saved_stdout = sys.stdout
        try:
            out = StringIO.StringIO()
            sys.stdout = out
            result = view_func(*args, **kwargs)
            output = out.getvalue().strip()
        finally:
            sys.stdout = saved_stdout
        return result, output
    return _view_func


class TestConfigCommands(TestCase):
    def setUp(self):
        self.prestocfg = PrestoCfg()
        self.config = load_config(TEST_CONFIG_NAME)
        self.prestocfg.cfg = load_config(TEST_CONFIG_NAME)

    @patch("presto.config_utils.PrestoCfg.load")
    def test_provider_list(self, mock_load):
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
        for provider in self.config['providers']:
            self.assertTrue(provider['name'] in output, 
                            'Provider %s not found' % provider['name'])
            provider_count += 1
        self.assertTrue(provider_count, 2)

    def test_add_provider(self):
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
        self.assertTrue("Added new provider %s" % (name) in output)

        provider = self.prestocfg.get_provider_by_name(name)
        for key, val in kwargs.iteritems():
            self.assertEquals(provider[key], val)

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
        for provider in self.config['providers']:
            for app in provider['apps']:
                self.assertTrue(app['name'] in output, 
                            'App %s not found' % app['name'])
                apps_count += 1
        self.assertTrue(apps_count, 3)

    def test_app_list_by_provider(self):
        """
        Tests `app_list_by_provider` command.
        """
        @intercept_output
        def app_list_by_provider(provider):
            return self.prestocfg.app_list_by_provider(provider)

        providers = self.config['providers']
        provider = random.choice(providers)
        result, output = app_list_by_provider(provider)
        self.assertEqual(result, None, 
                         'Nothing should be returned')
        apps_count = 0
        for app in provider['apps']:
            self.assertTrue(app['name'] in output, 
                        'App %s not found' % app['name'])
            apps_count += 1
        self.assertTrue(apps_count, len(provider['apps']))

    def test_app_add(self):
        pass

    def token_add(self):
        pass

    def test_get_provider_by_id(self):
        self.assertRaises(PrestoCfgException, 
                          self.prestocfg.get_provider_by_id, -1)
        self.assertRaises(PrestoCfgException, 
                          self.prestocfg.get_provider_by_id, 'a')
        self.assertRaises(PrestoCfgException, 
                          self.prestocfg.get_provider_by_id, 1000)

        provider = self.prestocfg.get_provider_by_id(1)
        provider_in_config = self.config['providers'][0]
        self.assertEquals(provider_in_config, provider)

        prestocfg = PrestoCfg()
        prestocfg.cfg = json.loads('{}')
        self.assertRaises(PrestoCfgException, prestocfg.get_provider_by_id, 1)
