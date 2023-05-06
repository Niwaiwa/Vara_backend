# Generated by Django 4.1.8 on 2023-05-05 15:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.commons
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageSlide',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('rating', models.CharField(choices=[('G', 'General'), ('E', 'Ecchi')], default='G', max_length=2)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('likes_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', models.ManyToManyField(blank=True, related_name='taged_image_slides', to='content.tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_slides', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image_file', models.ImageField(upload_to=utils.commons.UniqueFilename('images/'))),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='content.imageslide')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]