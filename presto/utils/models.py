from copy import deepcopy
import simplejson as json
from presto.utils.fields import Field, MultipleObjectsField, FormField
from presto.utils.exceptions import ValidationError


def get_declared_fields(bases, attrs):
    """
    Create a list of Model field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases').
    """
    fields = [(field_name, attrs.pop(field_name)) \
              for field_name, obj in attrs.items() \
                if isinstance(obj, Field)]
    fields.sort(key=lambda x: x[1].creation_counter)

    for base in bases[::-1]:
        if hasattr(base, 'declared_fields'):
            fields = base.declared_fields.items() + fields

    return fields


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = get_declared_fields(bases, attrs)
        return super(DeclarativeFieldsMetaclass,
                     cls).__new__(cls, name, bases, attrs)


class Model(object):
    "A collection of Fields, plus their associated data."
    __metaclass__ = DeclarativeFieldsMetaclass

    def __init__(self, data=None, parent=None):
        self.data = data or {}
        self.parent = parent

        self.fields = deepcopy(self.base_fields)
        fields = dict(self.fields)
        for name, item in self.data.iteritems():
            if fields.has_key(name):
                field = fields[name]
                field.value = self.data.get(name, field.DEFAULT_VALUE)

    def __getattr__(self, name):
        fields = dict(self.fields)
        if fields.has_key(name):
            return fields[name].value
        return  object.__getattribute__(self, name)

    def __unicode__(self):
        return "Data Model:" % self.data

    @property
    def errors(self):
        "Returns an errors for the data provided for the Model"
        if not hasattr(self, '_errors'):
            self.clean()
        return self._errors

    def is_valid(self):
        """
        Returns True if the Model has no errors. Otherwise, False.
        """
        self.clean()
        return not bool(self.errors)

    def clean(self):
        self._errors = {}
        self.cleaned_data = {}
        for name, field in self.fields:
            if type(field) is MultipleObjectsField:
                continue

            kwargs = {}
            if hasattr(self, 'validate_%s' % name):
                kwargs['validation_func'] = getattr(self, 'validate_%s' % name)

            if hasattr(self, 'get_text_%s' % name):
                kwargs['text_func'] = getattr(self, 'get_text_%s' % name)

            if hasattr(self, 'get_extra_params_%s' % name):
                kwargs.update(getattr(self, 'get_extra_params_%s' % name)())

            try:
                self.cleaned_data[name] = field.clean(**kwargs)
            except ValidationError, exc:
                self._errors[name] = exc.messages

        self.from_dict(self.cleaned_data)

    def to_dict(self):
        dict = {}
        for fieldname, field in self.fields:
            if type(field) is FormField:
                continue

            value = field.value
            if isinstance(value, (list, tuple)):
                dict[fieldname] = [val.to_dict() for val in value]
            else:
                dict[fieldname] = value
        return dict

    def from_dict(self, dict):
        for fieldname, field in self.fields:
            if type(field) is FormField:
                continue

            value = dict.get(fieldname, field.DEFAULT_VALUE)
            field.set_value(value, parent=self)

    def filter(self, fieldname, **kwargs):
        def apply_filters(item, **kwargs):
            for fieldname, value in kwargs.iteritems():
                if getattr(item, fieldname) != value:
                    return False
            return True

        items = getattr(self, fieldname)
        for item in items:
            if apply_filters(item, **kwargs):
                return item
        return None