# Generated by Django 4.2.3 on 2023-07-23 18:16

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0003_rename_admin_administrator'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='announcement',
            name='acknowledgement',
        ),
        migrations.RemoveField(
            model_name='announcement',
            name='student',
        ),
        migrations.CreateModel(
            name='AnnouncementAcknowledgement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acknowledgement', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
                ('announcement', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='app1.announcement')),
                ('student', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='app1.student')),
            ],
        ),
    ]