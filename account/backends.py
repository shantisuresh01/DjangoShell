import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from djangotailoring.accounts.models import GroupAccessCode

logger = logging.getLogger(__name__)


class AccessCodeBackend(ModelBackend):
    groupcode_class = GroupAccessCode
    
    def authenticate(self, accesscode=None):
        try:
            logger.info('Checking for individual access code.')
            user = get_user_model().objects.get(accesscode__code=accesscode)
            if not (user.has_usable_password()) and user.is_active:
                logger.info('User authenticated.')
                return user
            logger.info('User with access code has completed account setup.')
        except get_user_model().DoesNotExist:
            logger.info('No user with access code found.')
            return None
        return None
    

class temp_EmailOrUsernameBackend(ModelBackend):
    ''' Slightly modify ModelBackend's authenticate method to handle email or username '''
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except:
                user = UserModel._default_manager.get(username=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
