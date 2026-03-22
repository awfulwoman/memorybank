from django.db import migrations


def create_default_currencies(apps, schema_editor):
    Currency = apps.get_model('core', 'Currency')
    defaults = [
        ('EUR', '€', 'Euro'),
        ('GBP', '£', 'British Pound'),
        ('USD', '$', 'US Dollar'),
    ]
    for code, symbol, name in defaults:
        Currency.objects.get_or_create(code=code, defaults={'symbol': symbol, 'name': name})


def reverse_default_currencies(apps, schema_editor):
    Currency = apps.get_model('core', 'Currency')
    Currency.objects.filter(code__in=['EUR', 'GBP', 'USD']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_category_icon_group_icon'),
    ]

    operations = [
        migrations.RunPython(create_default_currencies, reverse_default_currencies),
    ]
