from django.contrib import admin
from lists import models


admin.site.register(models.ShoppingList)
admin.site.register(models.Item)
