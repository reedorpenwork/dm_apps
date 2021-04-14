from django.test import tag
from django.urls import reverse_lazy
from faker import Factory

from shared_models.test.common_tests import CommonTest
from shared_models.views import CommonCreateView, CommonFilterView, CommonUpdateView, CommonDeleteView, CommonDetailView, CommonFormView, \
    CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView
from . import FactoryFloor
from .. import models
from ..views import biofouling_views, shared_views

faker = Factory.create()




class TestSampleCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.site = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:sample_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Sample", "sample_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleCreateView, CommonCreateView)

    @tag("Sample", "sample_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Sample", "sample_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_new", f"/en/grais/samples/new/")


class TestSampleDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:sample_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Sample", "sample_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleDeleteView, CommonDeleteView)

    @tag("Sample", "sample_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Sample.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Sample", "sample_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_delete", f"/en/grais/samples/{self.instance.pk}/delete/", [self.instance.pk])


class TestSampleDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:sample_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/sample_detail/main.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Sample", "sample_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleDetailView, CommonDetailView)

    @tag("Sample", "sample_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_detail", f"/en/grais/samples/{self.instance.pk}/view/", [self.instance.pk])


class TestSampleUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:sample_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Sample", "sample_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleUpdateView, CommonUpdateView)

    @tag("Sample", "sample_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Sample", "sample_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_edit", f"/en/grais/samples/{self.instance.pk}/edit/", [self.instance.pk])


class TestSpeciesCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:species_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_new", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesCreateView, CommonCreateView)

    @tag("Species", "species_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Species", "species_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:species_new", f"/en/grais/species/new/")


class TestSpeciesDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('grais:species_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesDeleteView, CommonDeleteView)

    @tag("Species", "species_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Species.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Species", "species_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:species_delete", f"/en/grais/species/{self.instance.pk}/delete/", [self.instance.pk])


class TestSpeciesDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('grais:species_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/species_detail.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesDetailView, CommonDetailView)

    @tag("Species", "species_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:species_detail", f"/en/grais/species/{self.instance.pk}/view/", [self.instance.pk])


class TestSpeciesListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:species_list')
        self.expected_template = 'grais/list.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_list", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesListView, CommonFilterView)

    @tag("Species", "species_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Species", "species_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:species_list", f"/en/grais/species/")


class TestSpeciesUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('grais:species_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesUpdateView, CommonUpdateView)

    @tag("Species", "species_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Species", "species_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:species_edit", f"/en/grais/species/{self.instance.pk}/edit/", [self.instance.pk])





class TestStationCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.site = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:station_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationCreateView, CommonCreateView)

    @tag("Station", "station_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_new", "submit")
    def test_submit(self):
        data = FactoryFloor.StationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Station", "station_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_new", f"/en/grais/stations/new/")


class TestStationDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StationFactory()
        self.test_url = reverse_lazy('grais:station_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationDeleteView, CommonDeleteView)

    @tag("Station", "station_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.StationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Station.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Station", "station_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_delete", f"/en/grais/stations/{self.instance.pk}/delete/", [self.instance.pk])


class TestStationDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StationFactory()
        self.test_url = reverse_lazy('grais:station_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/station_detail/main.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationDetailView, CommonDetailView)

    @tag("Station", "station_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_detail", f"/en/grais/stations/{self.instance.pk}/view/", [self.instance.pk])


class TestStationUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StationFactory()
        self.test_url = reverse_lazy('grais:station_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationUpdateView, CommonUpdateView)

    @tag("Station", "station_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.StationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Station", "station_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_edit", f"/en/grais/stations/{self.instance.pk}/edit/", [self.instance.pk])



# 
# 
# class TestCollectionCreateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:collection_new')
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("Collection", "collection_new", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.CollectionCreateView, CommonCreateView)
# 
#     @tag("Collection", "collection_new", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("Collection", "collection_new", "submit")
#     def test_submit(self):
#         data = FactoryFloor.CollectionFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("Collection", "collection_new", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:collection_new", f"/en/grais/collections/new/")
# 
# 
# class TestCollectionDeleteView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.CollectionFactory()
#         self.test_url = reverse_lazy('grais:collection_delete', args=[self.instance.pk, ])
#         self.expected_template = 'grais/confirm_delete.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("Collection", "collection_delete", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.CollectionDeleteView, CommonDeleteView)
# 
#     @tag("Collection", "collection_delete", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("Collection", "collection_delete", "submit")
#     def test_submit(self):
#         data = FactoryFloor.CollectionFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#         # for delete views...
#         self.assertEqual(models.Collection.objects.filter(pk=self.instance.pk).count(), 0)
# 
#     @tag("Collection", "collection_delete", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:collection_delete", f"/en/grais/collections/{self.instance.pk}/delete/", [self.instance.pk])
# 
# 
# class TestCollectionDetailView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.CollectionFactory()
#         self.test_url = reverse_lazy('grais:collection_detail', args=[self.instance.pk, ])
#         self.expected_template = 'grais/collection_detail.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("Collection", "collection_detail", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.CollectionDetailView, CommonDetailView)
# 
#     @tag("Collection", "collection_detail", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("Collection", "collection_detail", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:collection_detail", f"/en/grais/collections/{self.instance.pk}/view/", [self.instance.pk])
# 
# 
# class TestCollectionListView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:collection_list')
#         self.expected_template = 'grais/list.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("Collection", "collection_list", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.CollectionListView, CommonFilterView)
# 
#     @tag("Collection", "collection_list", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("Collection", "collection_list", "context")
#     def test_context(self):
#         context_vars = [
#             "field_list",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)
# 
#     @tag("Collection", "collection_list", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:collection_list", f"/en/grais/collections/")
# 
# 
# class TestCollectionUpdateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.CollectionFactory()
#         self.test_url = reverse_lazy('grais:collection_edit', args=[self.instance.pk, ])
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("Collection", "collection_edit", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.CollectionUpdateView, CommonUpdateView)
# 
#     @tag("Collection", "collection_edit", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("Collection", "collection_edit", "submit")
#     def test_submit(self):
#         data = FactoryFloor.CollectionFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("Collection", "collection_edit", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:collection_edit", f"/en/grais/collections/{self.instance.pk}/edit/", [self.instance.pk])
# 
# 
# class TestExtractionBatchCreateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:extraction_batch_new')
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("ExtractionBatch", "extraction_batch_new", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.ExtractionBatchCreateView, CommonCreateView)
# 
#     @tag("ExtractionBatch", "extraction_batch_new", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_new", "submit")
#     def test_submit(self):
#         data = FactoryFloor.ExtractionBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_new", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:extraction_batch_new", f"/en/grais/extractions/new/")
# 
# 
# class TestExtractionBatchDeleteView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.ExtractionBatchFactory()
#         self.test_url = reverse_lazy('grais:extraction_batch_delete', args=[self.instance.pk, ])
#         self.expected_template = 'grais/confirm_delete.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("ExtractionBatch", "extraction_batch_delete", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.ExtractionBatchDeleteView, CommonDeleteView)
# 
#     @tag("ExtractionBatch", "extraction_batch_delete", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_delete", "submit")
#     def test_submit(self):
#         data = FactoryFloor.ExtractionBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#         # for delete views...
#         self.assertEqual(models.ExtractionBatch.objects.filter(pk=self.instance.pk).count(), 0)
# 
#     @tag("ExtractionBatch", "extraction_batch_delete", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:extraction_batch_delete", f"/en/grais/extractions/{self.instance.pk}/delete/", [self.instance.pk])
# 
# 
# class TestExtractionBatchDetailView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.ExtractionBatchFactory()
#         self.test_url = reverse_lazy('grais:extraction_batch_detail', args=[self.instance.pk, ])
#         self.expected_template = 'grais/extraction_batch_detail.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("ExtractionBatch", "extraction_batch_detail", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.ExtractionBatchDetailView, CommonDetailView)
# 
#     @tag("ExtractionBatch", "extraction_batch_detail", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_detail", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:extraction_batch_detail", f"/en/grais/extractions/{self.instance.pk}/view/", [self.instance.pk])
# 
# 
# class TestExtractionBatchListView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:extraction_batch_list')
#         self.expected_template = 'grais/list.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("ExtractionBatch", "extraction_batch_list", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.ExtractionBatchListView, CommonFilterView)
# 
#     @tag("ExtractionBatch", "extraction_batch_list", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_list", "context")
#     def test_context(self):
#         context_vars = [
#             "field_list",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_list", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:extraction_batch_list", f"/en/grais/extractions/")
# 
# 
# class TestExtractionBatchUpdateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.ExtractionBatchFactory()
#         self.test_url = reverse_lazy('grais:extraction_batch_edit', args=[self.instance.pk, ])
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("ExtractionBatch", "extraction_batch_edit", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.ExtractionBatchUpdateView, CommonUpdateView)
# 
#     @tag("ExtractionBatch", "extraction_batch_edit", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_edit", "submit")
#     def test_submit(self):
#         data = FactoryFloor.ExtractionBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("ExtractionBatch", "extraction_batch_edit", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:extraction_batch_edit", f"/en/grais/extractions/{self.instance.pk}/edit/", [self.instance.pk])
# 
# 
# class TestFileCreateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.CollectionFactory()
#         self.test_url = reverse_lazy('grais:file_new', args=[self.instance.pk, ])
#         self.expected_template = 'shared_models/generic_popout_form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("File", "file_new", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FileCreateView, CommonPopoutCreateView)
# 
#     @tag("File", "file_new", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("File", "file_new", "submit")
#     def test_submit(self):
#         data = FactoryFloor.FileFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user, file_field_name="file")
# 
#     @tag("File", "file_new", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:file_new", f"/en/grais/collections/{self.instance.pk}/new-file/", [self.instance.pk])
# 
# 
# class TestFileDeleteView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.FileFactory()
#         self.test_url = reverse_lazy('grais:file_delete', args=[self.instance.pk, ])
#         self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("File", "file_delete", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FileDeleteView, CommonPopoutDeleteView)
# 
#     @tag("File", "file_delete", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("File", "file_delete", "submit")
#     def test_submit(self):
#         data = FactoryFloor.FileFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#         # for delete views...
#         self.assertEqual(models.File.objects.filter(pk=self.instance.pk).count(), 0)
# 
#     @tag("File", "file_delete", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:file_delete", f"/en/grais/files/{self.instance.pk}/delete/", [self.instance.pk])
# 
# 
# class TestFileUpdateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.FileFactory()
#         self.test_url = reverse_lazy('grais:file_edit', args=[self.instance.pk, ])
#         self.expected_template = 'shared_models/generic_popout_form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("File", "file_edit", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FileUpdateView, CommonPopoutUpdateView)
# 
#     @tag("File", "file_edit", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("File", "file_edit", "submit")
#     def test_submit(self):
#         data = FactoryFloor.FileFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("File", "file_edit", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:file_edit", f"/en/grais/files/{self.instance.pk}/edit/", [self.instance.pk])
# 
# 
# class TestFiltrationBatchCreateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:filtration_batch_new')
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("FiltrationBatch", "filtration_batch_new", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FiltrationBatchCreateView, CommonCreateView)
# 
#     @tag("FiltrationBatch", "filtration_batch_new", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_new", "submit")
#     def test_submit(self):
#         data = FactoryFloor.FiltrationBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_new", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:filtration_batch_new", f"/en/grais/filtrations/new/")
# 
# 
# class TestFiltrationBatchDeleteView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.FiltrationBatchFactory()
#         self.test_url = reverse_lazy('grais:filtration_batch_delete', args=[self.instance.pk, ])
#         self.expected_template = 'grais/confirm_delete.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("FiltrationBatch", "filtration_batch_delete", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FiltrationBatchDeleteView, CommonDeleteView)
# 
#     @tag("FiltrationBatch", "filtration_batch_delete", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_delete", "submit")
#     def test_submit(self):
#         data = FactoryFloor.FiltrationBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#         # for delete views...
#         self.assertEqual(models.FiltrationBatch.objects.filter(pk=self.instance.pk).count(), 0)
# 
#     @tag("FiltrationBatch", "filtration_batch_delete", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:filtration_batch_delete", f"/en/grais/filtrations/{self.instance.pk}/delete/", [self.instance.pk])
# 
# 
# class TestFiltrationBatchDetailView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.FiltrationBatchFactory()
#         self.test_url = reverse_lazy('grais:filtration_batch_detail', args=[self.instance.pk, ])
#         self.expected_template = 'grais/filtration_batch_detail.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("FiltrationBatch", "filtration_batch_detail", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FiltrationBatchDetailView, CommonDetailView)
# 
#     @tag("FiltrationBatch", "filtration_batch_detail", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_detail", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:filtration_batch_detail", f"/en/grais/filtrations/{self.instance.pk}/view/", [self.instance.pk])
# 
# 
# class TestFiltrationBatchListView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:filtration_batch_list')
#         self.expected_template = 'grais/list.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("FiltrationBatch", "filtration_batch_list", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FiltrationBatchListView, CommonFilterView)
# 
#     @tag("FiltrationBatch", "filtration_batch_list", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_list", "context")
#     def test_context(self):
#         context_vars = [
#             "field_list",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_list", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:filtration_batch_list", f"/en/grais/filtrations/")
# 
# 
# class TestFiltrationBatchUpdateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.FiltrationBatchFactory()
#         self.test_url = reverse_lazy('grais:filtration_batch_edit', args=[self.instance.pk, ])
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("FiltrationBatch", "filtration_batch_edit", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.FiltrationBatchUpdateView, CommonUpdateView)
# 
#     @tag("FiltrationBatch", "filtration_batch_edit", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_edit", "submit")
#     def test_submit(self):
#         data = FactoryFloor.FiltrationBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("FiltrationBatch", "filtration_batch_edit", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:filtration_batch_edit", f"/en/grais/filtrations/{self.instance.pk}/edit/", [self.instance.pk])
# 
# 
# class TestPCRBatchCreateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:pcr_batch_new')
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("PCRBatch", "pcr_batch_new", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.PCRBatchCreateView, CommonCreateView)
# 
#     @tag("PCRBatch", "pcr_batch_new", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_new", "submit")
#     def test_submit(self):
#         data = FactoryFloor.PCRBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_new", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:pcr_batch_new", f"/en/grais/pcrs/new/")
# 
# 
# class TestPCRBatchDeleteView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.PCRBatchFactory()
#         self.test_url = reverse_lazy('grais:pcr_batch_delete', args=[self.instance.pk, ])
#         self.expected_template = 'grais/confirm_delete.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("PCRBatch", "pcr_batch_delete", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.PCRBatchDeleteView, CommonDeleteView)
# 
#     @tag("PCRBatch", "pcr_batch_delete", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_delete", "submit")
#     def test_submit(self):
#         data = FactoryFloor.PCRBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#         # for delete views...
#         self.assertEqual(models.PCRBatch.objects.filter(pk=self.instance.pk).count(), 0)
# 
#     @tag("PCRBatch", "pcr_batch_delete", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:pcr_batch_delete", f"/en/grais/pcrs/{self.instance.pk}/delete/", [self.instance.pk])
# 
# 
# class TestPCRBatchDetailView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.PCRBatchFactory()
#         self.test_url = reverse_lazy('grais:pcr_batch_detail', args=[self.instance.pk, ])
#         self.expected_template = 'grais/pcr_batch_detail.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("PCRBatch", "pcr_batch_detail", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.PCRBatchDetailView, CommonDetailView)
# 
#     @tag("PCRBatch", "pcr_batch_detail", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_detail", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:pcr_batch_detail", f"/en/grais/pcrs/{self.instance.pk}/view/", [self.instance.pk])
# 
# 
# class TestPCRBatchListView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.test_url = reverse_lazy('grais:pcr_batch_list')
#         self.expected_template = 'grais/list.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("PCRBatch", "pcr_batch_list", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.PCRBatchListView, CommonFilterView)
# 
#     @tag("PCRBatch", "pcr_batch_list", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_list", "context")
#     def test_context(self):
#         context_vars = [
#             "field_list",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_list", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:pcr_batch_list", f"/en/grais/pcrs/")
# 
# 
# class TestPCRBatchUpdateView(CommonTest):
#     def setUp(self):
#         super().setUp()
#         self.instance = FactoryFloor.PCRBatchFactory()
#         self.test_url = reverse_lazy('grais:pcr_batch_edit', args=[self.instance.pk, ])
#         self.expected_template = 'grais/form.html'
#         self.user = self.get_and_login_user(in_group="grais_admin")
# 
#     @tag("PCRBatch", "pcr_batch_edit", "view")
#     def test_view_class(self):
#         self.assert_inheritance(biofouling_views.PCRBatchUpdateView, CommonUpdateView)
# 
#     @tag("PCRBatch", "pcr_batch_edit", "access")
#     def test_view(self):
#         self.assert_good_response(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_edit", "submit")
#     def test_submit(self):
#         data = FactoryFloor.PCRBatchFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data, user=self.user)
# 
#     @tag("PCRBatch", "pcr_batch_edit", "correct_url")
#     def test_correct_url(self):
#         # use the 'en' locale prefix to url
#         self.assert_correct_url("grais:pcr_batch_edit", f"/en/grais/pcrs/{self.instance.pk}/edit/", [self.instance.pk])
# 

class TestReportSearchFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:reports')
        self.expected_template = 'grais/report_search.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("ReportSearch", "reports", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.ReportSearchFormView, CommonFormView)

    @tag("ReportSearch", "reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReportSearch", "reports", "submit")
    def test_submit(self):
        data = dict(report=1)
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ReportSearch", "reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:reports", f"/en/grais/reports/")
