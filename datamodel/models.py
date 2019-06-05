'''
Created on May 25, 2019

@author: shanti
'''
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            is_active=True,
            date_joined=timezone.now(),
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(
            email=email,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class EventManager(models.Manager):
    def with_counts(self):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT u.id, u.email, e.name, COUNT(*)
            FROM datamodel_participant u, djangotailoring_event e
            WHERE u.id = e.user_id and e.name LIKE "%UserLoggedIn%"
            GROUP BY u.id, e.name
            ORDER BY e.timestamp DESC""")
        result_list = []
        for row in cursor.fetchall():
            u = self.model(id=row[0], email=row[1])
            u.name = row[2]
            u.count = row[3]
            result_list.append(u)
        return result_list
    
class User(AbstractBaseUser):

    USERNAME_FIELD = 'email'

    objects = UserManager()
    login_events = EventManager()
    
    email = models.EmailField('email', unique=True)
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    is_staff = models.BooleanField('staff status', default=False,
                                   help_text='Designates whether the user can log into this admin '
                                               'site.')
    is_active = models.BooleanField('active', default=True,
                                    help_text='Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting account.')

    def get_full_name(self):
        full_name = str(self.email)
        return full_name

    def __str__(self):
        return self.get_full_name()

    @property
    def username(self):
        full_name = self.email
        return full_name
    
    @property
    def userid(self):
        return self.id
        