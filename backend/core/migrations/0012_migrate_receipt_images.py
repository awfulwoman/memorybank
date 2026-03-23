from django.db import migrations


def copy_receipt_images(apps, schema_editor):
    Expense = apps.get_model('core', 'Expense')
    ReceiptImage = apps.get_model('core', 'ReceiptImage')
    for expense in Expense.objects.exclude(receipt_image='').exclude(receipt_image__isnull=True):
        ReceiptImage.objects.create(expense=expense, image=expense.receipt_image)


def reverse_copy(apps, schema_editor):
    ReceiptImage = apps.get_model('core', 'ReceiptImage')
    ReceiptImage.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_receiptimage'),
    ]

    operations = [
        migrations.RunPython(copy_receipt_images, reverse_copy),
    ]
