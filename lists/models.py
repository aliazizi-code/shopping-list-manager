from decimal import Decimal

from django.db import models
from django.db.models import Sum, F
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class ShoppingList(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('List name'))
    slug = models.SlugField(max_length=150, unique=True, editable=False, verbose_name=_('Slug'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lists', verbose_name=_('User'))

    @property
    def total_price(self):
        return (
                self.items
                .annotate(total_item_price=F('price') * F('quantity'))
                .aggregate(total=Sum('total_item_price'))
                ['total'] or Decimal(0)
        )

    @property
    def total_price_purchased(self):
        return (
            self.items
            .filter(is_purchased=True)
            .annotate(total_item_price=F('price') * F('quantity'))
            .aggregate(total=Sum('total_item_price'))
            ['total'] or Decimal(0)
        )

    @property
    def total_price_pending(self):
        return (
            self.items
            .filter(is_purchased=False)
            .annotate(total_item_price=F('price') * F('quantity'))
            .aggregate(total=Sum('total_item_price'))
            ['total'] or Decimal(0)
        )

    @property
    def total_items(self):
        return self.items.count()

    @property
    def purchased_items(self):
        return self.items.filter(is_purchased=True).count()

    @property
    def pending_items(self):
        return self.items.filter(is_purchased=False).count()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = _('List')
        verbose_name_plural = _('Lists')


class Item(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Item name'))
    slug = models.SlugField(max_length=150, unique=True, editable=False, verbose_name=_('Slug'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Price'))
    is_purchased = models.BooleanField(default=False, verbose_name=_('Purchased Status'))
    list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items', verbose_name=_('List'))

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != self.name:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['is_purchased', '-id']
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
