from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import UsernameValidator


class User(AbstractUser):
    email = models.EmailField(
        _('email'),
        max_length=254,
        unique=True
    )

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer.'
                    ' Letters, digits and @/./+/-/_ only.'),
        validator = UsernameValidator(
            regex=r'^[\w.@+-]+$',
        ),
        error_messages={
            'unique': _('A user with that username already exists.')
        },
    )
    first_name = models.CharField(
        _('name'),
        max_length=150
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150
    )
    password = models.CharField(
        _('password'),
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Follow(models.Model):
    pass
