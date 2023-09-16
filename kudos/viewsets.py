from rest_framework.response import Response

from kudos.models import Employee, Kudos
from rest_framework import viewsets
from rest_framework.decorators import action
from kudos.serializers import UserSerializer, KudosSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return self.queryset.filter(company_id=self.request.user.company_id)

    @action(methods=['get'], detail=True)
    def kudos(self, request, pk=None):
        qs = Kudos.objects.filter(to_id=pk)
        kudos = KudosSerializer(qs, many=True)
        return Response(kudos.data)


class KudosViewSet(viewsets.ModelViewSet):
    queryset = Kudos.objects.all()
    serializer_class = KudosSerializer
    http_method_names = ['post']
    ordering = ['-created_at']
