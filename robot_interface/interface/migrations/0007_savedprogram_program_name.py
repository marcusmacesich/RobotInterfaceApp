# Generated by Django 5.1.2 on 2025-04-02 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0006_websocketip'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedprogram',
            name='program_name',
            field=models.TextField(default='none'),
            preserve_default=False,
        ),
    ]
