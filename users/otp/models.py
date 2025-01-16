from django.db import models

from users.models.User import User


class UserCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.phone} - {self.otp} - {self.created_at}'