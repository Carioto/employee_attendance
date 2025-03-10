# Generated by Django 5.1.6 on 2025-03-04 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancerecord',
            name='code',
            field=models.CharField(choices=[('OFF', 'Not Scheduled'), ('NS', 'No call no show'), ('CO', 'Calling Off with Notice'), ('LCO', 'Calling Off Without Notice'), ('L', 'Late ( >10 minutes)'), ('XL', 'Excessively Late (>30 minutes)'), ('P', 'Present'), ('HRO', 'Hero')], max_length=3),
        ),
    ]
