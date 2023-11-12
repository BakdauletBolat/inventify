from django.contrib.auth.models import User
from django.db.models.base import ModelBase

from base.services.get_current_user import get_current_user
from history.models.History import History


def create_history(sender: ModelBase, instance, type, **kwargs):
    user = get_current_user()
    edits = {
        'attributes': {},
        'many_to_many': {}
    }
    match type:
        case 'single':
            action = 'created'
            if kwargs.get('created') is False:
                action = 'edit'
                edits['attributes'] = list(kwargs.get('update_fields'))
        case 'many_to_many':
            action = kwargs.get('action')
            edits['many_to_many'][kwargs.get('model').__name__] = list(kwargs.get('pk_set'))

    History.objects.create(
        action=action,
        content_object=instance,
        edits=edits,
        user=user if isinstance(user, User) else None
    )
