from presto.utils.utils import output, input
from presto.utils.exceptions import ValidationError, AlreadyExist


class Field(object):
    creation_counter = 0
    auto_creation_counter = -1
    DEFAULT_VALUE = None

    def __init__(self, value=None, required=True,
                 text='Please input', default=''):
        self.value = value
        self.required = required
        self.text = text
        self.default = default

        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def set_value(self, value, **kwargs):
        self._val = value

    def get_value(self):
        if not hasattr(self, '_val'):
            self._val= None
        return self._val

    value = property(get_value, set_value)

    def clean(self, validation_func=None, **kwargs):
        def validate_fn(value):
            if not value and self.default:
                value = self.default

            if self.required and not value:
                raise ValidationError('Field is required.')
            if not validation_func is None:
                value = validation_func(value)
            return value

        value = self.value
        try:
            return self.validate(value, validate_fn)
        except ValidationError, AlreadyExist:
            return self.question(text=self.text,
                                  default=self.default,
                                  validation_func=validate_fn,
                                  **kwargs)

    def validate(self, value, validation_func=None):
        if validation_func is None:
            return value

        return validation_func(value)

    def question(self, text, default=None, 
                 validation_func=None, 
                 ext_func=None, ext_param={}):
        output(text + ':')
        if ext_func:
            ext_func(**ext_param)

        while True:
            value = unicode(input()).strip()
            try:
                value = self.validate(value, validation_func)
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
        while True:
            self.output_func("Rewrite '%s'? (y/n)" % value)
            yes_no = unicode(self.input_func())
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

    def validate(self, value, validation_func=None):
        value = super(ChoiceField, self).validate(value, validation_func)
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
