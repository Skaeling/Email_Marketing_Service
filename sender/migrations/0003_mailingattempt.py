# Generated by Django 5.1.3 on 2024-11-21 18:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0002_alter_newsletter_recipients_alter_recipient_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailingAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempt_date', models.DateTimeField(verbose_name='Дата и время попытки')),
                ('exc_state', models.CharField(choices=[('success', 'Успешно'), ('error', 'Не успешно')], max_length=15, verbose_name='Статус отправки')),
                ('server_response', models.TextField()),
                ('newsletter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mailing_attempts', to='sender.newsletter')),
            ],
            options={
                'verbose_name': 'попытка',
                'verbose_name_plural': 'попытки',
                'ordering': ['exc_state'],
            },
        ),
    ]
