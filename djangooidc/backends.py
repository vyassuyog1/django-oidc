from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class OpenIdConnectBackend(ModelBackend):
    """
    This backend is to be used in conjunction with the ``OpenIdUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.
    """

    def authenticate(self, **userinfo):
        """
        To authenticate engage the OpenId Connect login procedure.
        The username returned by this process is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        print 'RRRRRRRRRRRRRRRRRRRR'
        print userinfo
        if not userinfo or 'sub' not in userinfo.keys():
            print 'YYYYYYYYYYY'
            return
        user = None

        UserModel = get_user_model()

        username = self.clean_username(userinfo['sub'])
        if 'upn' in userinfo.keys():
            username = userinfo['upn']

        # Some OP may actually choose to withhold some information, so we must test if it is present
        openid_data = {UserModel.USERNAME_FIELD: username}
        if 'first_name' in userinfo.keys():
            openid_data['first_name'] = userinfo['first_name']
        if 'family_name' in userinfo.keys():
            openid_data['last_name'] = userinfo['family_name']
        if 'given_name' in userinfo.keys():
            openid_data['last_name'] = userinfo['given_name']
        if 'email' in userinfo.keys():
            openid_data['email'] = userinfo['email']

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if getattr(settings, 'OIDC_CREATE_UNKNOWN_USER', True):
            user, created = UserModel.objects.get_or_create(**openid_data)
            if created:
                user = self.configure_user(user)
        else:
            try:
                user = UserModel.objects.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                pass
        return user

    def clean_username(self, username):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """
        return username

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        return user