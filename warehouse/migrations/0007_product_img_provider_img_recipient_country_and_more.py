# Generated by Django 5.0.1 on 2024-04-20 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0006_alter_coming_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='img',
            field=models.ImageField(default='static/images/profile.png', upload_to='images/'),
        ),
        migrations.AddField(
            model_name='provider',
            name='img',
            field=models.ImageField(default='static/images/profile.png', upload_to='images/'),
        ),
        migrations.AddField(
            model_name='recipient',
            name='country',
            field=models.CharField(default='Қазақстан', max_length=50, verbose_name='Страна'),
        ),
        migrations.AddField(
            model_name='recipient',
            name='img',
            field=models.ImageField(default='static/images/profile.png', upload_to='images/'),
        ),
    ]