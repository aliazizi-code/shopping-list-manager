# Generated by Django 5.1.3 on 2024-12-10 11:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='List name')),
                ('slug', models.SlugField(editable=False, max_length=150, unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lists', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'List',
                'verbose_name_plural': 'Lists',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Item name')),
                ('slug', models.SlugField(editable=False, max_length=150, unique=True, verbose_name='Slug')),
                ('quantity', models.IntegerField(verbose_name='Quantity')),
                ('price', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Price')),
                ('is_purchased', models.BooleanField(default=False, verbose_name='Purchased Status')),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='lists.shoppinglist', verbose_name='List')),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
                'ordering': ['is_purchased', '-id'],
            },
        ),
    ]