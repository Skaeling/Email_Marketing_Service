from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='user_images/', default='user_images/default_avatar.png', blank=True, null=True,
                               help_text='Изображение размером не более 5 мб')
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text='Введите только цифры')
    country = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['email', ]
        permissions = [
            ('can_view_all_users', 'Can view all users'),
            ('can_block_user', 'Can block user')
        ]
