# Generated by Django 5.1.6 on 2025-03-08 12:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedbackApp', '0004_alter_yemekyorumu_yemek'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='yurt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='yurt', to='feedbackApp.yurt'),
        ),
        migrations.AddField(
            model_name='yemekyorumu',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='media/yemek_foto/'),
        ),
    ]
