# Generated by Django 3.1 on 2022-07-07 04:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('department', '0002_auto_20220707_0145'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('about', models.TextField(blank=True, max_length=500)),
                ('price', models.IntegerField()),
                ('image', models.ImageField(upload_to='photos/doctors')),
                ('slots', models.IntegerField()),
                ('is_available', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='department.department')),
            ],
        ),
    ]
