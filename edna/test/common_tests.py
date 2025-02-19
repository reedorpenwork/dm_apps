import os

from shared_models.test.common_tests import CommonTest
from ..models import ednaUser


# here are common tests for Travel. Essentially they will just load the travel fixutres
class CommonEDNATest(CommonTest):

    def get_and_login_user(self, user=None, in_group=None, is_superuser=False, is_admin=False, is_crud_user=False, is_read_only=False):
        user = super().get_and_login_user(user, in_group, is_superuser)
        if is_read_only:
            ednaUser.objects.get_or_create(user=user)
        else:
            if is_admin:
                u = ednaUser.objects.get_or_create(user=user)[0]
                u.is_admin = True
                u.save()
            if is_crud_user:
                u = ednaUser.objects.get_or_create(user=user)[0]
                u.is_crud_user = True
                u.save()
        return user
