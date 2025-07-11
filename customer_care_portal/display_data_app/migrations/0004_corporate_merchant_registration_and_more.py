# Generated by Django 5.0.7 on 2024-08-25 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('display_data_app', '0003_user_profile_sqr_data_download'),
    ]

    operations = [
        migrations.CreateModel(
            name='corporate_merchant_registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet', models.CharField(max_length=11)),
                ('qr_sticker_name', models.CharField(max_length=500)),
                ('qr_display_name', models.CharField(max_length=500)),
                ('business_type', models.CharField(max_length=500)),
                ('account_manager_nid_number', models.CharField(max_length=17)),
                ('account_manager_dob', models.CharField(max_length=500)),
                ('account_manager_face_photo', models.CharField(max_length=1000)),
                ('account_manager_nid_photo_front', models.CharField(max_length=1000)),
                ('account_manager_nid_photo_back', models.CharField(max_length=1000)),
                ('is_active', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_by_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='user_profile',
            name='corporate_merchant_registration',
            field=models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], default='NO', max_length=10),
        ),
    ]
