import os
import simplejson as json
from oauthlib.oauth1.rfc5849 import SIGNATURE_TYPE_QUERY

from presto.utils.models import Model
from presto.utils.exceptions import ValidationError
from presto.utils.fields import (MultipleObjectsField, UrlField, ChoiceField,
    DomainField, FormField, CharField)


PRESTO_CONFIG_FILE_NAME = os.path.join(os.getenv("HOME"), ".presto")


class Token(Model):
    provider = FormField(text='Choose the provider')
    app = FormField(text='Choose the application')
    name = CharField(
            text="Enter the name of the authorization ['default']",
            default="default"
    )
    request_tokens = FormField(required=False)
    token_key = CharField()
    token_secret = CharField(required=False)

    def validate_provider(self, provider):
        return self.parent.get_provider_by_positional_num(provider)

    def get_extra_params_provider(self):
        return {'ext_func': lambda: self.parent.provider_list(), }

    def validate_app(self, app):
        provider = self.cleaned_data['provider']
        return provider.get_app_by_id(app)

    def get_extra_params_app(self):
        provider = self.cleaned_data['provider']
        return {'ext_func': lambda: provider.app_list(), }

    def validate_name(self, name):
        app = self.cleaned_data['app']
        if app.tokens:
            for token in app.tokens:
                if token.name == name:
                    raise ValidationError(
                        "Token with name '%s' already exist on app '%s'." \
                                                        % (name, app.name)
                    )
        return name

    def validate_request_tokens(self, tokens):
        from presto.oauth import get_request_token
        app = self.cleaned_data['app']
        provider = self.cleaned_data['provider']
        return get_request_token(
          app.public_key,
          app.secret_key,
          provider.request_token_url,
          provider.request_token_method
        )

    def get_text_token_key(self):
        from presto.oauth import build_authorize_url
        provider = self.cleaned_data['provider']
        request_tokens = self.cleaned_data['request_tokens']
        url = build_authorize_url(provider.auth_url, request_tokens[0])
        return "Paste this URL to your browser: '%s'\nEnter 'oauth_verifier' that you got" % url

    def validate_token_key(self, verifier):
        from presto.oauth import get_access_token
        provider = self.cleaned_data['provider']
        app = self.cleaned_data['app']
        request_tokens = self.cleaned_data['request_tokens']
        token, self.secret = get_access_token(
             request_tokens[0], 
             request_tokens[1],
             provider.access_token_url, 
             provider.access_token_method,
             app.public_key,
             app.secret_key,
             verifier
        )
        return token

    def validate_token_secret(self, secret):
        # FIXME: Remove this hack. Save auth tokens in one field as list.
        return self.secret


class Application(Model):
    provider = FormField(text='Choose the provider')
    name = CharField(text="Enter the name of the app ['default']",
                           default='default'
    )
    public_key = CharField(text="Enter the public key")
    secret_key = CharField(text="Enter the secret key")
    tokens = MultipleObjectsField(Token)

    def validate_provider(self, provider):
        '''
        Checks that provider exist in the config.
        
        :param provider: provider positional number.
        '''
        return self.parent.get_provider_by_positional_num(provider)

    def validate_name(self, name):
        provider = self.cleaned_data['provider']
        for app in provider.apps:
            if app.name == name:
                raise ValidationError('App with same name already exist.')
        return name

    def get_extra_params_provider(self):
        return {'ext_func': lambda: self.parent.provider_list(), }


class Provider(Model):
    METHOD_CHOICES = ('POST', 'GET')
    AUTH_TYPES = ('OAuth1.0', 'OAuth2.0')

    name = CharField(
        text="Enter the name of the provider (e.g. 'odesk')"
    )
    domain_name = DomainField(
        text="Enter the domain name (may be comma-separated list)"
    )
    auth_type = ChoiceField(
        text="Enter the auth type: OAuth1.0 or [OAuth2.0]",
        choices=('OAuth1.0', 'OAuth2.0'),
        default='OAuth2.0'
    )

    # Tokens
    request_token_method = ChoiceField(text="Request token method ['POST']",
                                       choices=METHOD_CHOICES, default='POST')
    request_token_url = UrlField(text="Request token URL")

    access_token_method = ChoiceField(text="Access token method ['POST']",
                                      choices=METHOD_CHOICES, default='POST')
    access_token_url = UrlField(text="Access token URL")

    auth_url = UrlField(text="Auth URL")
    apps = MultipleObjectsField(Application)

    def validate_name(self, name):
        conf = self.parent
        for provider in conf.providers:
            if provider.name == name:
                raise ValidationError(\
                        "Provider with name '%s' already exist." % name)
        return name

    def app_list(self):
        for i, app in enumerate(self.apps):
            print "[%d] %s (%s)" % (i + 1, app.name, self.name)

    def get_app_by_id(self, app):
        if not app.isdigit():
            raise ValidationError("App argument must be integer.")
        app = int(app)

        apps = self.apps
        if not apps:
            raise ValueError("Please add app.")

        if app <= len(apps) and app > 0:
            app = apps[app - 1]
        else:
            raise ValidationError("Provider must be from 1 to %d." % len(apps))

        return app


class Configuration(Model):
    providers = MultipleObjectsField(Provider)

    def load_from_file(self, file_name=PRESTO_CONFIG_FILE_NAME):
        if os.path.exists(file_name):
            f = file(file_name, "r")
            cfg = f.read()
            f.close()
        else:
            f = file(file_name, "w+")
            f_template = open(os.path.join(os.path.dirname(__file__), 'presto.cfg'))
            cfg = f_template.read()
            f_template.close()
            f.write(cfg)
            f.close()
        if cfg:
            cfg = json.loads(cfg)
        else:
            raise PrestoCfgException("Empty configuration file")

        self.from_dict(cfg)

    def save_to_file(self, filepath=PRESTO_CONFIG_FILE_NAME):
        conf = self.to_dict()
        cfg_file = open(filepath, 'w')
        cfg_json = json.dumps(conf, sort_keys=True, indent=4 * ' ')
        cfg_json = '\n'.join([l.rstrip() for l in  cfg_json.splitlines()])
        cfg_file.write(cfg_json)
        cfg_file.close()

    def get_provider_by_positional_num(self, provider):
        if not provider.isdigit():
            raise ValidationError("Provider argument must be integer.")

        provider = int(provider)
        providers = self.providers

        if provider <= len(providers) and provider > 0:
            provider = providers[provider - 1]
        else:
            raise ValidationError("Provider must be from 1 to %d." % len(providers))
        return provider

    def provider_list(self):
        for i, provider in enumerate(self.providers):
            print "[%d] %s" % (i + 1, provider.name)
        print ""


config = Configuration()
config.load_from_file()
