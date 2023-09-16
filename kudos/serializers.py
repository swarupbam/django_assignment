from rest_framework import serializers
from kudos.models import Employee, Company, Kudos


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Employee
        fields = ['id', 'username', 'date_joined', 'company']


class KudosSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(source='from_id', read_only=True)

    class Meta:
        model = Kudos
        fields = ['from_id', 'to_id', 'message', 'created_at', 'from_user']
        extra_kwargs = {'from_id': {'write_only': True}, 'to_id': {'write_only': True}}
