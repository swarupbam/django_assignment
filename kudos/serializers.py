from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from djangoProject.settings import DEFAULT_KUDOS_PER_WEEK
from kudos.models import Employee, Company, Kudos, UserKudosCounter
import arrow


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

    def validate(self, attrs):
        super(KudosSerializer, self).validate(attrs)
        user_kudos_info = UserKudosCounter.objects.filter(user_id=attrs['from_id']).last()
        last_given_kudos_date = arrow.get(user_kudos_info.updated_at)
        now = arrow.now()
        start_of_this_week, end_of_this_week = now.span('week')

        # Check if it's a new week
        if start_of_this_week <= last_given_kudos_date <= end_of_this_week:
            if user_kudos_info.counter == 0:
                raise PermissionDenied("Limit exceeded")
            else:
                attrs['is_new_week'] = False
        else:
            attrs['is_new_week'] = True
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user_counter = UserKudosCounter.objects.get(user_id=validated_data['from_id'])
        remaining_kudos = DEFAULT_KUDOS_PER_WEEK if validated_data['is_new_week'] is True else user_counter.counter
        kudos = Kudos.objects.create(from_id=validated_data['from_id'], to_id=validated_data['to_id'],
                                     message=validated_data.get('message'))
        user_counter.counter = remaining_kudos - 1
        user_counter.save()
        return kudos
