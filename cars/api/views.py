from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .. import models, filters

class CalendarRSVPListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = models.Reservation.objects.filter(~Q(status=20))
    serializer_class = serializers.CalendarRSVPSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.ReservationFilter


# class CSASRequestViewSet(viewsets.ModelViewSet):
#     queryset = models.Reservation.objects.all()
#     serializer_class = serializers.CSASRequestSerializer
#     # permission_classes = [CanModifyRequestOrReadOnly]
#     # pagination_class = StandardResultsSetPagination
#     #
#     # def get_queryset(self):
#     #     qs = models.CSASRequest.objects.all()
#     #     qs = qs.annotate(search=Concat('title', Value(" "), 'translated_title', Value(" "), 'id', output_field=TextField()))
#     #     return qs
#     #
#     # def post(self, request, pk):
#     #     qp = request.query_params
#     #     csas_request = get_object_or_404(models.CSASRequest, pk=pk)
#     #     if qp.get("withdraw"):
#     #         if utils.is_client(request.user, pk) or utils.can_modify_request(request.user, pk, True):
#     #             csas_request.withdraw()
#     #             return Response(serializers.CSASRequestSerializer(csas_request).data, status.HTTP_200_OK)
#     #         raise ValidationError(_("Sorry, you do not have permissions to withdraw this request"))
#     #     raise ValidationError(_("This endpoint cannot be used without a query param"))
#
#     def list(self, request, *args, **kwargs):
#         qp = request.GET
#         if qp.get("as_resource_list"):
#             pass
#
#         return
#
