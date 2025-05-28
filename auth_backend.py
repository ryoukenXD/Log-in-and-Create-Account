from django.contrib.auth.backends import BaseBackend
from .models import Account

class PlainTextAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Account.objects.get(username=username)
            if user.password == password:  # Compare plain text passwords
                return user
        except Account.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Account.objects.get(pk=user_id)
        except Account.DoesNotExist:
            return None 