# Generated by Django 2.2.5 on 2019-12-08 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Enquete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enquete_id', models.CharField(max_length=100)),
                ('enquete_name', models.CharField(max_length=100)),
            ],
        ),
    ]
