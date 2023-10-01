from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
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
        validators = [
            UsernameValidator(
                regex=r'^[\w.@+-]+$',
            ),
            RegexValidator(
                regex=r'^(?!me$)',
                message=_('Username cannot be "me".')
            ),
        ],
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

    def __str__(self):
        return self.email


class Follow(models.Model):
    
    follower = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name=_('follower')
    )

    author = models.ForeignKey(
        User,
        related_name='author',
        on_delete=models.CASCADE,
        verbose_name=_('author')
    )

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return _(f'{self.follower} subscribed to: {self.author}')
