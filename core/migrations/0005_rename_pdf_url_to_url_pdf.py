# Generated migration to rename pdf_url to url_pdf

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_document_checksum_document_pdf_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='pdf_url',
            new_name='url_pdf',
        ),
    ]