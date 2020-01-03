# Generated by Django 2.2.5 on 2020-01-01 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enquete', '0002_auto_20191229_2135'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='QM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=512)),
                ('M_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enquete.Member')),
                ('Q_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enquete.Question')),
            ],
        ),
    ]
