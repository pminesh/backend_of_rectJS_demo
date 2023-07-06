from enum import unique
from django.db import models
from django.forms import CharField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from model_utils import Choices
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from rest_framework_simplejwt.tokens import RefreshToken

# model for user
# # 05/Oct/2022 Minesh patel
# # ===============================================================================Start
# class UserModel(models.Model):
#     USER_TYPES = Choices(
#         ("A","Admin"),
#         ("U","User"),
#         ("SA","Super User"),
#     )

#     username_validator = UnicodeUsernameValidator()

#     user_name = models.CharField(
#         _('user name'),
#         max_length=150,
#         unique=True,
#         blank=True,
#         null=True,
#         help_text=(
#             'Required: 150 characters or fewer. Lettres , digits and @/./+/-/ only .'),
#         validators=[username_validator],
#         error_messages={
#             'unique': _('A user with that username already exists.'),
#         }
#     )
#     user_email = models.EmailField(
#         _('user email'),
#         null=True,
#         blank=True,
#         unique=True,
#         error_messages={
#             'unique': _('A user with that email address  already exists.'),
#         }
#     )
#     user_password = models.CharField(
#         _('user password'),
#         max_length=16,
#         validators=[MinLengthValidator(8)],
#         help_text=('Required 16 maximum characters or minimum 8.'),
#         error_messages={
#             'unique': _('Please password must be between 8-16 characters.'),
#         }
#     )

#     user_type = models.CharField(max_length=10, choices=USER_TYPES)

#     class Meta:
#         verbose_name = _('User')
#         db_table = 'automation_user'

#     def __str__(self):
#         return f'{self.user_name}'
# # ===============================================================================End


class MyUserManager(BaseUserManager):
    def create_user(self, email, user_name, mobile_number,password=None,password2=None,**extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not user_name:
            raise ValueError('Users should have a username')

        if not email:
            raise ValueError('User must have an email address')

        extra_fields.setdefault('is_admin', False)

        user = self.model(
            email=self.normalize_email(email),
            user_name=user_name,
            mobile_number=mobile_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_name,mobile_number, password=None,**extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        extra_fields.setdefault('is_admin', True)
        
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        user = self.create_user(
            email,
            password=password,
            user_name=user_name,
            mobile_number=mobile_number,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    user_name = models.CharField(
        _('user name'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text=(
            'Required: 150 characters or fewer. Lettres , digits and @/./+/-/ only .'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        }
    )
    
    mobile_number = models.CharField(_('mobile number'),max_length=255,unique=True,blank=True,null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_(
            'Designates whether this user email is verified. '
        ),
    )

    mobile_verified = models.BooleanField(
        _('mobile verified'),
        default=False,
        help_text=_(
            'Designates whether this user mobile is verified. '
        ),
    )

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name','mobile_number']

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
