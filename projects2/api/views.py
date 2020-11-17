from django.contrib.auth.models import User
from pandas import date_range
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions
from . import serializers
from .. import models, stat_holidays
from ..utils import financial_project_year_summary_data, financial_project_summary_data, get_user_fte_breakdown, can_modify_project
from shared_models import models as shared_models

# USER
#######
class CurrentUserAPIView(APIView):
    def get(self, request):
        serializer = serializers.UserDisplaySerializer(instance=request.user)
        data = serializer.data
        if request.query_params.get("project"):
            data.update(can_modify_project(request.user, request.query_params.get("project"), True))
        return Response(data)


class FTEBreakdownAPIView(APIView):
    def get(self, request):
        # if no user is specified, we will assume it is the request user
        if not request.query_params.get("user"):
            my_user = request.user
        else:
            my_user = get_object_or_404(User, pk=request.query_params.get("user"))

        # if there is no fiscal year specified, let's get all years
        if not request.query_params.get("year"):
            # need a list of fiscal years
            fy_qs = shared_models.FiscalYear.objects.filter(projectyear__staff__user=my_user).distinct()
            data = list()
            for fy in fy_qs:
                data.append(get_user_fte_breakdown(my_user, fiscal_year_id=fy.id))
        else:
            data = get_user_fte_breakdown(my_user, fiscal_year_id=request.query_params.get("year"))
        return Response(data, status.HTTP_200_OK)


class GetDatesAPIView(APIView):
    def get(self, request):
        fiscal_year = self.request.query_params.get("year")  # to be formatted as follows: YYYY; SAP style
        if fiscal_year:
            fiscal_year = int(fiscal_year)
            # create a pandas date_range object for upcoming fiscal year
            start = f"{fiscal_year - 1}-04-01"
            end = f"{fiscal_year}-03-31"
            datelist = date_range(start=start, end=end).tolist()

            date_format = "%d-%B-%Y"
            short_date_format = "%d-%b-%Y"
            # get a list of statutory holidays
            holiday_list = [d.strftime(date_format) for d in stat_holidays.stat_holiday_list]

            data = list()
            # create a dict for the response
            for dt in datelist:
                is_stat = dt.strftime(date_format) in holiday_list
                weekday = dt.strftime("%A")
                int_weekday = dt.strftime("%w")
                obj = dict(
                    formatted_date=dt.strftime(date_format),
                    formatted_short_date=dt.strftime(short_date_format),
                    weekday=weekday,
                    short_weekday=f'{dt.strftime("%a")}.',
                    int_weekday=int_weekday,
                    is_stat=is_stat,
                    pay_rate=2 if is_stat or int_weekday == 0 else 1.5
                )
                data.append(obj)
            return Response(data, status.HTTP_200_OK)
        raise ValidationError("missing query parameter 'year'")


class ProjectYearRetrieveAPIView(RetrieveAPIView):
    queryset = models.ProjectYear.objects.all().order_by("-created_at")
    serializer_class = serializers.ProjectYearSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# STAFF
#######
class StaffListCreateAPIView(ListCreateAPIView):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.staff_set.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))

    # def post(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)


class StaffRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# O&M
#######
class OMCostListCreateAPIView(ListCreateAPIView):
    queryset = models.OMCost.objects.all()
    serializer_class = serializers.OMCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.omcost_set.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))

    # def post(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)


class OMCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.OMCost.objects.all()
    serializer_class = serializers.OMCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


class AddAllCostsAPIView(APIView):
    permission_classes = [permissions.CanModifyOrReadOnly]

    def post(self, request, project_year):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        year.add_all_om_costs()
        serializer = serializers.OMCostSerializer(instance=year.omcost_set.all(), many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class RemoveEmptyCostsAPIView(APIView):
    permission_classes = [permissions.CanModifyOrReadOnly]

    def post(self, request, project_year):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        year.clear_empty_om_costs()
        serializer = serializers.OMCostSerializer(instance=year.omcost_set.all(), many=True)
        return Response(serializer.data, status.HTTP_200_OK)


# CAPITAL
#########
class CapitalCostListCreateAPIView(ListCreateAPIView):
    queryset = models.CapitalCost.objects.all()
    serializer_class = serializers.CapitalCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.capitalcost_set.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class CapitalCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.CapitalCost.objects.all()
    serializer_class = serializers.CapitalCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# GC
####

class GCCostListCreateAPIView(ListCreateAPIView):
    queryset = models.GCCost.objects.all()
    serializer_class = serializers.GCCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.gc_costs.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class GCCostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.GCCost.objects.all()
    serializer_class = serializers.GCCostSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# MILESTONE
###########
class MilestoneListCreateAPIView(ListCreateAPIView):
    queryset = models.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.milestones.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class MilestoneRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# COLLABORATOR
##############
class CollaboratorListCreateAPIView(ListCreateAPIView):
    queryset = models.Collaborator.objects.all()
    serializer_class = serializers.CollaboratorSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.collaborators.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class CollaboratorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.Collaborator.objects.all()
    serializer_class = serializers.CollaboratorSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# AGREEMENTS
##############
class AgreementListCreateAPIView(ListCreateAPIView):
    queryset = models.CollaborativeAgreement.objects.all()
    serializer_class = serializers.AgreementSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.agreements.all()

    def perform_create(self, serializer):
        serializer.save(project_year_id=self.kwargs.get("project_year"))


class AgreementRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.CollaborativeAgreement.objects.all()
    serializer_class = serializers.AgreementSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# FILES / Supporting Resources
##############
class FileListCreateAPIView(ListCreateAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]

    def get_queryset(self):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        return year.files.all()

    def perform_create(self, serializer):
        year = models.ProjectYear.objects.get(pk=self.kwargs.get("project_year"))
        serializer.save(project=year.project, project_year=year)

        if self.request.FILES:
            print(self.request.FILES)


class FileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    permission_classes = [permissions.CanModifyOrReadOnly]


# FINANCIALS
############


class FinancialsAPIView(APIView):
    permissions = [IsAuthenticated]
    def get(self, request, project_year=None, project=None):
        if not project_year and not project:
            return Response(None, status.HTTP_400_BAD_REQUEST)

        if project_year:
            obj = get_object_or_404(models.ProjectYear, pk=project_year)
            data = financial_project_year_summary_data(obj)

        else:  # must be supplied with a project
            obj = get_object_or_404(models.Project, pk=project)
            data = financial_project_summary_data(obj)

        return Response(data, status.HTTP_200_OK)
