from django.test import tag
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate

from .common_tests import ScubaCommonTest as CommonTest
from ..test import FactoryFloor
from shared_models.views import CommonFormsetView, CommonHardDeleteView
from .. import views
from .. import models
from faker import Factory

faker = Factory.create()

#
# class TestAllFormsets(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url_names = [
#             "manage_divers",
#         ]
#
#         self.test_urls = [reverse_lazy("scuba:" + name) for name in self.test_url_names]
#         self.test_views = [
#             views.DiverFormsetView,
#         ]
#         self.expected_template = 'scuba/formset.html'
#         self.user = self.get_and_login_admin()
#
#     @tag('formsets', "view")
#     def test_view_class(self):
#         for v in self.test_views:
#             self.assert_inheritance(v, views.ScubaAdminRequiredMixin)
#             self.assert_inheritance(v, CommonFormsetView)
#
#     @tag('formsets', "access")
#     def test_view(self):
#         for url in self.test_urls:
#             self.assert_good_response(url)
#             self.assert_non_public_view(test_url=url, expected_template=self.expected_template, user=self.user)
#
#     @tag('formsets', "submit")
#     def test_submit(self):
#         data = dict()  # should be fine to submit with empty data
#         for url in self.test_urls:
#             self.assert_success_url(url, data=data)
#
#
# class TestAllHardDeleteViews(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.starter_dicts = [
#             {"model": models.Diver, "url_name": "delete_diver", "view": views.DiverHardDeleteView},
#         ]
#         self.test_dicts = list()
#
#         self.user = self.get_and_login_admin()
#         for d in self.starter_dicts:
#             new_d = d
#             m = d["model"]
#             if m == models.Diver:
#                 obj = FactoryFloor.DiverFactory()
#             else:
#                 obj = m.objects.create(name=faker.word())
#             new_d["obj"] = obj
#             new_d["url"] = reverse_lazy("scuba:" + d["url_name"], kwargs={"pk": obj.id})
#             self.test_dicts.append(new_d)
#
#     @tag('hard_delete', "view")
#     def test_view_class(self):
#         for d in self.test_dicts:
#             self.assert_inheritance(d["view"], views.ScubaAdminRequiredMixin)
#             self.assert_inheritance(d["view"], CommonHardDeleteView)
#
#     @tag('hard_delete', "access")
#     def test_view(self):
#         for d in self.test_dicts:
#             self.assert_good_response(d["url"])
#             # only have one chance to test this url
#             self.assert_non_public_view(test_url=d["url"], user=self.user, expected_code=302, locales=["en"])
#
#     @tag('hard_delete', "delete")
#     def test_delete(self):
#         # need to be an admin user to do this
#         self.get_and_login_user(user=self.user)
#         for d in self.test_dicts:
#             # start off to confirm the object exists
#             self.assertIn(d["obj"], type(d["obj"]).objects.all())
#             # visit the url
#             activate("en")
#             self.client.get(d["url"])
#             # confirm the object has been deleted
#             self.assertNotIn(d["obj"], type(d["obj"]).objects.all())
