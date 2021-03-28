from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)

    # Cents
    price = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.name

    def get_display_price(self):
        return '{0:.2f}'.format(self.price / 100)
