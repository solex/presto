import os
import simplejson as json
from presto.utils.models import Model
from presto.utils.exceptions import ValidationError
from presto.utils.fields import (MultipleObjectsField, UrlField, ChoiceField,
    DomainField, FormField, CharField)


PRESTO_CONFIG_FILE_NAME = '/home/atmel/workspace/presto/presto/tests/test_presto.cfg'


class Application(Model):
    provider = FormField(text='Choose the provider')
    name = CharField(text="Enter the name of the app ['default']",
                           default='default'
    )
    public_key = CharField(text="Enter the public key")
    secret_key = CharField(text="Enter the secret key")

    def validate_provider(self, provider):
        '''
        Checks that provider exist in the config.
        
        :param provider: provider positional number.
        '''
        if not provider.isdigit():
            raise ValidationError("Provider argument must be integer.")

        provider = int(provider)
        cfg = self.parent
        providers = cfg.providers

        if provider <= len(providers) and provider > 0:
            provider = providers[provider - 1]
        else:
            raise ValidationError("Provider must be from 1 to %d." % len(providers))
        return provider

    def validate_name(self, name):
        provider = self.cleaned_data['provider']
        for app in provider.apps:
            if app.name == name:
                raise ValidationError('App with same name already exist.')
        return name

    def get_extra_params_provider(self):
        def show_provider_list():
            for i, provider in enumerate(self.parent.providers):
                print "[%d] %s" % (i + 1, provider.name)
            print ""

        return {'ext_func': show_provider_list, }


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

config = Configuration()
config.load_from_file()
