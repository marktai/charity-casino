# Generated by Django 4.0.4 on 2022-06-24 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_wordlist_board_word_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='wordlist',
            name='adult',
            field=models.BooleanField(default=False),
        ),
    ]
