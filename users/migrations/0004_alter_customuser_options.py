# Generated by Django 5.1.3 on 2024-12-18 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': [('can_view_all_users', 'Can view all users'), ('can_block_user', 'Can block user')]},
        ),
    ]
