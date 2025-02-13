from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.views.generic import TemplateView

from shared_models.models import Organization
from shared_models.test.SharedModelsFactoryFloor import UserFactory
from travel.test import FactoryFloor
from travel.test.common_tests import CommonTravelTest as CommonTest
from shared_models.views import CommonFormsetView, CommonHardDeleteView
from .. import views
from .. import models
from faker import Factory

faker = Factory.create()


class TestAllFormsets(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url_names = [
            "manage_help_text",
            "manage_cost_categories",
            "manage_costs",
            "manage_njc_rates",
            "manage_trip_subcategories",
            "manage_trip_categories",
            "manage_roles",
            "manage_process_steps",
            "manage_faqs",
            "manage_organizations",
            "manage_travel_users",
        ]

        self.test_urls = [reverse_lazy("travel:" + name) for name in self.test_url_names]
        self.test_views = [
            views.HelpTextFormsetView,
            views.CostCategoryFormsetView,
            views.CostFormsetView,
            views.NJCRatesFormsetView,
            views.TripSubcategoryFormsetView,
            views.TripCategoryFormsetView,
            views.RoleFormsetView,
            views.ProcessStepFormsetView,
            views.FAQFormsetView,
            views.OrganizationFormsetView,
            views.TravelUserFormsetView,
        ]
        self.expected_template = 'travel/formset.html'
        self.user = self.get_and_login_admin()

    @tag('formsets', "view")
    def test_view_class(self):
        for v in self.test_views:
            if v is views.TravelUserFormsetView:
                self.assert_inheritance(v, views.SuperuserOrNationalAdminRequiredMixin)
            else:
                self.assert_inheritance(v, views.TravelADMAdminRequiredMixin)
            self.assert_inheritance(v, CommonFormsetView)

    @tag('formsets', "access")
    def test_view(self):
        for url in self.test_urls:
            self.assert_good_response(url)
            self.assert_non_public_view(test_url=url, expected_template=self.expected_template, user=self.user)

    @tag('formsets', "submit")
    def test_submit(self):
        data = dict()  # should be fine to submit with empty data
        for url in self.test_urls:
            self.assert_success_url(url, data=data)


class TestAllHardDeleteViews(CommonTest):
    def setUp(self):
        super().setUp()
        self.starter_dicts = [
            {"model": models.HelpText, "url_name": "delete_help_text", "view": views.HelpTextHardDeleteView},
            {"model": models.Cost, "url_name": "delete_cost", "view": views.CostHardDeleteView},
            {"model": models.CostCategory, "url_name": "delete_cost_category", "view": views.CostCategoryHardDeleteView},
            {"model": models.TripSubcategory, "url_name": "delete_trip_subcategory", "view": views.TripSubcategoryHardDeleteView},
            {"model": models.Role, "url_name": "delete_role", "view": views.RoleHardDeleteView},
            {"model": models.ProcessStep, "url_name": "delete_process_step", "view": views.ProcessStepHardDeleteView},
            {"model": models.FAQ, "url_name": "delete_faq", "view": views.FAQHardDeleteView},
            {"model": Organization, "url_name": "delete_organization", "view": views.OrganizationHardDeleteView},
            {"model": models.TravelUser, "url_name": "delete_travel_user", "view": views.TravelUserHardDeleteView},
        ]
        self.test_dicts = list()

        self.user = self.get_and_login_admin()
        for d in self.starter_dicts:
            new_d = d
            m = d["model"]
            if m == models.HelpText:
                obj = m.objects.create(field_name=faker.word(), eng_text=faker.word())
            elif m == models.Cost:
                cc = models.CostCategory.objects.all()[faker.random_int(0, models.CostCategory.objects.count() - 1)]
                obj = m.objects.create(name=faker.word(), cost_category=cc)
            elif m == models.TripSubcategory:
                tc = models.TripCategory.objects.all()[faker.random_int(0, models.TripCategory.objects.count() - 1)]
                obj = m.objects.create(name=faker.word(), trip_category=tc)
            elif m == models.FAQ:
                obj = m.objects.create(question_en=faker.catch_phrase())
            elif m == models.TravelUser:
                obj = m.objects.create(user=UserFactory())
            else:
                obj = m.objects.create(name=faker.word())
            new_d["obj"] = obj
            new_d["url"] = reverse_lazy("travel:" + d["url_name"], kwargs={"pk": obj.id})
            self.test_dicts.append(new_d)

    @tag('hard_delete', "view")
    def test_view_class(self):
        for d in self.test_dicts:
            if d["view"] is views.TravelUserHardDeleteView:
                self.assert_inheritance(d["view"], views.SuperuserOrNationalAdminRequiredMixin)
            else:
                self.assert_inheritance(d["view"], views.TravelADMAdminRequiredMixin)
            self.assert_inheritance(d["view"], CommonHardDeleteView)

    @tag('hard_delete', "access")
    def test_view(self):
        for d in self.test_dicts:
            self.assert_good_response(d["url"])
            # only have one chance to test this url
            self.assert_non_public_view(test_url=d["url"], user=self.user, expected_code=302, locales=["en"])

    @tag('hard_delete', "delete")
    def test_delete(self):
        # need to be an admin user to do this
        self.get_and_login_user(user=self.user)
        for d in self.test_dicts:
            # start off to confirm the object exists
            self.assertIn(d["obj"], type(d["obj"]).objects.all())
            # visit the url
            activate("en")
            self.client.get(d["url"])
            # confirm the object has been deleted
            self.assertNotIn(d["obj"], type(d["obj"]).objects.all())
