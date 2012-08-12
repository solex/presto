from presto.utils.utils import output
from presto.utils.exceptions import ValidationError, AlreadyExist


class Field(object):
    creation_counter = 0
    auto_creation_counter = -1
    DEFAULT_VALUE = None

    def __init__(self, value=None, required=True,
                 text=None, default=''):
        self.value = value
        self.required = required

        self.text = text
        self.default = default

        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1
        self.validation_func = None

    def set_value(self, value, **kwargs):
        self._val = unicode(value or '').strip()

    def get_value(self):
        if not hasattr(self, '_val'):
            self._val = self.DEFAULT_VALUE
        return self._val

    value = property(get_value, set_value)

    def clean(self, validation_func=None, 
                    text_func=None, **kwargs):
        self.validation_func = validation_func
        try:
            if self.required and not self.value:
                raise ValidationError('Field is required.')

            return self.validate(self.value)
        except (ValidationError, AlreadyExist):
            if not self.text and text_func:
                self.text = text_func()
            return self.question(text=self.text,
                                  default=self.default,
                                  **kwargs)

    def validate(self, value):
        if not value and self.default:
            value = self.default

        if self.required and not value:
            raise ValidationError('Field is required.')

        if self.validation_func is None:
            return value

        return self.validation_func(value)

    def question(self, text, default=None, 
                 ext_func=None, ext_param={}):
        from presto.utils.utils import input
        output("%s:" % text)
        if ext_func:
            ext_func(**ext_param)

        while True:
            value = unicode(input()).strip()
            try:
                value = self.validate(value)
            except AlreadyExist, e:
                self.output_func(e.messages)
                should_rewrite = self.yesno()
                if should_rewrite:
                    return value
                else:
                    raise
            except ValidationError, e:
                output(e.messages)
                continue
            return value

    def yesno(self):
        from presto.utils.utils import input
        while True:
            output("Rewrite '%s'? (y/n)" % value)
            yes_no = unicode(input())
            if yes_no in ('Y', 'y', 'yes', '\n'):
                return True
            if yes_no in ('N', 'n', 'no'):
                return False


class CharField(Field):
    pass

class UrlField(CharField):
    pass


class ChoiceField(CharField):
    def __init__(self, value=None, required=True,
                 text='Please input', default='', choices=(),
                 error_message=None):
        super(ChoiceField, self).__init__(value, required, text, 
                                          default)
        self.choices = choices
        self.error_message = error_message or \
                'Please specify valid choice: %s' % str(self.choices)

    def validate(self, value):
        value = super(ChoiceField, self).validate(value)
        if not value in self.choices:
            raise ValidationError(self.error_message)
        return value


class DomainField(CharField):
    pass


class MultipleObjectsField(Field):
    DEFAULT_VALUE = []

    def set_value(self, value, parent=None):
        res = []
        self.parent = parent
        for obj_dict in value or self.DEFAULT_VALUE:
            obj = self.model()
            obj.from_dict(obj_dict)
            obj.parent = self
            res.append(obj)
        self._val = res

    def get_value(self):
        if not hasattr(self, '_val'):
            return None

        return self._val

    value = property(get_value, set_value)
    def __init__(self, model):
        self.model = model
        super(MultipleObjectsField, self).__init__()


class FormField(Field):
    pass
