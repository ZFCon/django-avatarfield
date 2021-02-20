from django.db.models import ForeignKey

from .widget import AvatarModelChoiceField


class AvatarForeignKey(ForeignKey):
    def __init__(self, to, on_delete, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, image_field='avatar', **kwargs):
        self.image_field = image_field

        super().__init__(to, on_delete, related_name, related_query_name,
                         limit_choices_to, parent_link, to_field,
                         db_constraint, **kwargs)

    def formfield(self, *, using=None, **kwargs):
        if isinstance(self.remote_field.model, str):
            raise ValueError("Cannot create form field for %r yet, because "
                             "its related model %r has not been loaded yet" %
                             (self.name, self.remote_field.model))
        return super().formfield(**{
            'form_class': AvatarModelChoiceField,
            'queryset': self.remote_field.model._default_manager.using(using),
            'to_field_name': self.remote_field.field_name,
            'image_field': self.image_field,
            **kwargs,
            'blank': self.blank,
        })
