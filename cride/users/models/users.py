""" User model. """

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Utilities
from cride.utils.models import SRideModel

class User(SRideModel, AbstractUser):
    """ User model.
    Extends from Django's Abstract User, 
    change the username field to email and 
    add some extra fields.
    """

    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with that email already exists.'
        }
    )

    phone_regex = RegexValidator(
        regex='\+?1?\d{8,15}$',
        message='Phone number must be enterd in the format: +50769237843. Up to 15 digits allowed.'
    )
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[phone_regex]
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_client = models.BooleanField(
        'client status',
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries. '
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='Set to true when the user have verified its email address.'
    )

    def __str__(self):
        """ Return username. """
        return self.username

    def get_short_name(self):
        """ Return username. """
        return self.username
