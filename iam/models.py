from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser):
    uuid = models.UUIDField(unique=True, default=uuid4)
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # set custom manager
    objects = CustomUserManager()

    # set field used as username
    USERNAME_FIELD = 'email'

    # set required fields
    REQUIRED_FIELDS = []
