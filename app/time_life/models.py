from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta


class TimeLifeModel(models.Model):
    life = models.BooleanField(default=False)
    unique_hash = models.CharField(unique=True, max_length=255)
    times_life = ArrayField(models.JSONField(), default=list)
    average_life_time = models.DateTimeField(blank=True, null=True)

    def calculate_average_life_time(self):
        total_duration = 0
        count = 0

        for entry in self.times_life:
            start = entry.get('start')
            stop = entry.get('stop')

            if start is not None and stop is not None:
                duration = stop - start
                total_duration += duration
                count += 1

        if count > 0:
            self.average_life_time = timedelta(seconds=total_duration / count)

    def save(self, *args, **kwargs):
        self.calculate_average_life_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'TimeLifeModel #{self.id}'
