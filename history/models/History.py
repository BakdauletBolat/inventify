from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from base.models import BaseModel
from django.db import models

from django.conf import settings

User = settings.AUTH_USER_MODEL


class History(BaseModel):
    action = models.CharField(max_length=255)
    instance = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('instance', 'object_id')
    edits = models.JSONField(default=dict)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["instance", "object_id"]),
        ]
