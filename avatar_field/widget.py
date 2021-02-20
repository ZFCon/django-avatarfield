from django.forms import ModelChoiceField, Select
from django.forms.models import ModelChoiceIterator, ModelChoiceIteratorValue
from django.forms.fields import Field
from django.forms.widgets import RadioSelect


class AvatarModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field):
        self.field = field
        self.queryset = field.queryset
        # set image field to use it later to access image
        self.image_field = field.image_field

    def __iter__(self):
        if self.field.empty_label is not None:
            yield (None, "", self.field.empty_label)
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for obj in queryset:
            yield self.choice(obj)

    def choice(self, obj):
        choice = (
            getattr(obj, self.image_field),
            ModelChoiceIteratorValue(self.field.prepare_value(obj), obj),
            self.field.label_from_instance(obj),
        )

        return choice


class AvatarSelect(Select):
    template_name = 'avatar_field/widgets/select.html'
    option_template_name = 'avatar_field/widgets/select_option.html'

    class Media:
        css = {
            'all': [
                'avatar_field/css/bootstrap.css',
                'https://cdn.jsdelivr.net/npm/bootstrap-select@1.13.14/dist/css/bootstrap-select.min.css',
                'avatar_field/css/style.css',
            ]
        }
        js = [
            'https://code.jquery.com/jquery-3.3.1.slim.min.js',
            'avatar_field/js/bootstrap.min.js',
            'https://cdn.jsdelivr.net/npm/bootstrap-select@1.13.14/dist/js/bootstrap-select.min.js',
        ]

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False

        for index, (option_image, option_value, option_label) in enumerate(self.choices):
            if option_value is None:
                option_value = ''

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_image, option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for image, subvalue, sublabel in choices:
                selected = (
                    str(subvalue) in value and
                    (not has_selected or self.allow_multiple_selected)
                )
                has_selected |= selected
                subgroup.append(self.create_option(
                    name, image, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs,
                ))
                if subindex is not None:
                    subindex += 1
        return groups

    def create_option(self, name, image, value, label, selected, index, subindex=None, attrs=None):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(
            self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)

        return {
            'name': name,
            'image': image,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
            'wrap_label': True,
        }


class AvatarModelChoiceField(ModelChoiceField):
    widget = AvatarSelect
    iterator = AvatarModelChoiceIterator

    def __init__(self, queryset, *, empty_label="---------",
                 required=True, widget=None, label=None, initial=None,
                 help_text='', to_field_name=None, limit_choices_to=None,
                 blank=False, image_field, **kwargs):
        self.image_field = image_field  # set image field to access it later

        # Call Field instead of ChoiceField __init__() because we don't need
        # ChoiceField.__init__().
        Field.__init__(
            self, required=required, widget=widget, label=label,
            initial=initial, help_text=help_text, **kwargs
        )
        if (
            (required and initial is not None) or
            (isinstance(self.widget, RadioSelect) and not blank)
        ):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        self.queryset = queryset
        self.limit_choices_to = limit_choices_to   # limit the queryset later.
        self.to_field_name = to_field_name
