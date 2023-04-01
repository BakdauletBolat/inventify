from django.contrib.auth.models import User
from django.db.models.base import ModelBase

from base.services.get_current_user import get_current_user
from history.models.History import History


def create_history(sender: ModelBase, instance, action, type, **kwargs):
    user = get_current_user()
    edits = {
        'attributes': {},
        'many_to_many': {}
    }
    match type:
        case 'single':
            if instance.id is not None:
                old_instance = sender.objects.get(id=instance.id)
                for field in instance._meta.fields:
                    if getattr(instance, field.attname) != getattr(old_instance, field.attname):
                        edits['attributes'][field.name] = {
                            'from': getattr(old_instance, field.attname),
                            'to': getattr(instance, field.attname)
                        }
        case 'many_to_many':
            print(list(kwargs.get('pk_set')))
            edits['many_to_many'][sender.__name__] = {
                [action]: list(kwargs.get('pk_set'))
            }

    History.objects.create(
        action=action,
        content_object=instance,
        edits=edits,
        user=user if isinstance(user, User) else None
    )
