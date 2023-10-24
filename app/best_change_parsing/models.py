from django.db import models


class LinksExchangeInfo(models.Model):
    id = models.AutoField(primary_key=True)
    exchange_id = models.IntegerField(unique=True)
    exchange_name = models.CharField(max_length=40)

    info_reverse = models.FloatField(default=0)
    info_age = models.CharField(max_length=40, default='Zero')
    info_star = models.IntegerField(default=0)
    info_verification =  models.BooleanField(default=False)
    info_registration =  models.BooleanField(default=False)

    addition_floating = models.BooleanField(default=False)
    addition_verifying = models.BooleanField(default=False)
    addition_manual = models.BooleanField(default=False)
    addition_percent = models.BooleanField(default=False)
    addition_otherin = models.BooleanField(default=False)
    addition_reg = models.BooleanField(default=False)

    class Meta:
        db_table = 'links_exchange_info'
        indexes = [
            models.Index(fields=['id']),
        ]