""" Users serializers. """

# Django
from django.contrib.auth import authenticate, password_validation
from django.core.validators import RegexValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Django REST framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from cride.users.models import User, Profile

class UserModelSerializer(serializers.ModelSerializer):
    """ User model serializer. """

    class Meta:
        """ Meta class. """
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number'
        )



class UserLoginSerializer(serializers.Serializer):
    """ User login serializer. 

    Handle the login request data. """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """ Check credentials. """
        user = authenticate(username=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError('Invalid credentials.')

        if not user.is_verified:
            raise serializers.ValidationError("Account is not active yet :(")

        self.context['user'] = user
        return data 
        
    def create(self, data):
        """ Generate or retrieve new token. """
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key

class UserSignUpSerializer(serializers.Serializer):
    """ User sign up serializer. 
    
        Handle sign up data validation and user/profile creation.
    """

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    # username
    username = serializers.CharField(
        min_length = 4,
        max_length = 20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # phone number
    phone_regex = RegexValidator(
        regex='\+?1?\d{8,15}$',
        message='Phone number must be enterd in the format: +50769237843. Up to 15 digits allowed.'
    )
    phone_number = serializers.CharField(
        validators=[phone_regex]
    )

    # password
    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    # name 

    first_name = serializers.CharField(min_length=2, max_length=40)
    last_name = serializers.CharField(min_length=2, max_length=40)

    def validate(self, data):
        """ Verify passwords match. """
        passwd = data['password']
        passwd_conf = data['password_confirmation']

        if passwd != passwd_conf:
            raise serializers.ValidationErrors("Password don't match.")

        password_validation.validate_password(passwd)
        return data

    def create(self, data):
        """ Handle user/profile creation. """
        # delete password conf, not needed
        data.pop('password_confirmation')

        # create user and profile
        user = User.objects.create_user(**data, is_verified=False)
        Profile.objects.create(user=user)
        
        # send email confirmation to user
        self.send_confirmation_email(user)

        return user

    def send_confirmation_email(self, user):
        """ Send account verification link to given user. """
        verification_token = self.gen_verification_token(user)
        
        subject = 'Welcome @{}! Verify your account to start using ShareRide.'.format(user.username)
        from_email = 'ShareRide <noreply@shareride.com>'
        content = render_to_string(
            'emails/users/account_verification.html',
            {'token': verification_token, 'user':user}
        )

        # send email 
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(content, "text/html")
        msg.send()

        print("Sending email")

    def gen_verification_token(self, user):
        """ Create JWT token that the user can use to verify their account. """
        return 'abc'