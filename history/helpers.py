def get_old_instance(instance):
    if not instance.pk:
        return None
    return instance.__class__.objects.filter(pk=instance.pk).first()
