# Generated by Django 5.1.3 on 2025-03-16 13:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_alter_response_answer_answer_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question_options',
            name='questionid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='base.questions'),
        ),
    ]
