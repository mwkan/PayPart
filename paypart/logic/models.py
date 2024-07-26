from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=200)
    # bank = options
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    #modify depending on API input

    def __str__(self):
        return self.name


# Create your models here.
