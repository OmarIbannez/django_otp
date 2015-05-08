from django.db import models
from django.contrib.auth.models import User

class OtpUser(models.Model):
    user = models.OneToOneField(User)
    secret_key = models.CharField(max_length = 16, null=True)

    def __unicode__(self):
        return self.user.username