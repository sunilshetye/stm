# Generated by Django 4.2.3 on 2023-07-30 11:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_remove_announcement_acknowledgement_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acknowledgement', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=None, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='announcement',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.DeleteModel(
            name='AnnouncementAcknowledgement',
        ),
        migrations.AddField(
            model_name='notification',
            name='announcement',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='app1.announcement'),
        ),
        migrations.AddField(
            model_name='notification',
            name='student',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='app1.student'),
        ),
    ]
