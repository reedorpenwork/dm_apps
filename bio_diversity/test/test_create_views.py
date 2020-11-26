from django.test import tag

from django.urls import reverse_lazy
from django.test import TestCase
from django.utils.translation import activate

from .common_views import CommonCreateTest

from bio_diversity import views, forms, models

from . import BioFactoryFloor


@tag('Instdc', 'create')
class TestInstdcCreate(CommonCreateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = BioFactoryFloor.InstdcFactory.build_valid_data()
        self.test_url = reverse_lazy('bio_diversity:create_instdc')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        self.expected_success_url = reverse_lazy('shared_models:close_me_no_refresh')

        self.expected_view = views.InstdcCreate
        self.expected_form = forms.InstdcForm
