from datetime import datetime
from unittest.mock import patch
from django.test import TestCase

from djangoProject import settings
from kudos.factories import CompanyFactory, EmployeeFactory, UserKudosCounterFactory
from rest_framework.test import APIClient
from kudos.models import UserKudosCounter, Kudos, arrow


class BaseTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company1 = CompanyFactory()
        self.company2 = CompanyFactory()

        self.user1 = EmployeeFactory(company=self.company1)
        self.user2 = EmployeeFactory(company=self.company1)
        self.user3 = EmployeeFactory(company=self.company1)
        self.user4 = EmployeeFactory(company=self.company2)
        self.user5 = EmployeeFactory(company=self.company2)
        for u in [self.user1, self.user2, self.user3, self.user4, self.user5]:
            UserKudosCounterFactory(user_id=u)
            u.set_password("123!")
            u.save()


class KudosTest(BaseTest):
    def get_token(self, client, username, password):
        res = client.post("/api/login/", data={"username": username, "password": "123!"},
                          headers={"accept": "application/json"})
        return res.json()['token']

    def test_only_users_of_the_requesting_user_company_should_be_fetched(self):
        client = APIClient()
        token = self.get_token(client=client, username=self.user1.username, password="123!")
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.get('/api/users/', headers={"accept": "application/json"})
        res_json = response.json()
        self.assertEqual(len(res_json), 3)

    def test_user_should_be_able_to_give_kudos(self):
        client = APIClient()
        token = self.get_token(client=client, username=self.user1.username, password="123!")
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user2.id, 'message': 'True leader'})
        assert UserKudosCounter.objects.get(user_id=self.user1).counter == 2
        assert Kudos.objects.filter(from_id=self.user1.id, to_id=self.user2.id, message="True leader").exists()

    def test_get_user_kudos_by_user_id(self):
        client = APIClient()
        token = self.get_token(client=client, username=self.user3.username, password="123!")
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        Kudos.objects.create(from_id=self.user1, to_id=self.user3)
        Kudos.objects.create(from_id=self.user2, to_id=self.user3)
        response = client.get(f"/api/users/{self.user3.id}/kudos/", headers={"accept": "application/json"})
        res_json = response.json()
        self.assertEqual(len(res_json), 2)

    def test_user_should_not_allow_to_be_allowed_to_give_kudos(self):
        client = APIClient()
        token = self.get_token(client=client, username=self.user1.username, password="123!")
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user2.id, 'message': 'True leader'})
        client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user2.id, 'message': 'Thank you!'})
        client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user3.id})
        response = client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user3.id})
        assert response.status_code == 403
        assert UserKudosCounter.objects.get(user_id=self.user1).counter == 0

    @patch('arrow.now')
    def test_user_should_be_able_to_give_kudos_when_a_new_week_starts(self, mocked_arrow_now):
        mocked_arrow_now.return_value = arrow.Arrow(2023, 8, 14, tzinfo=settings.TIME_ZONE)
        UserKudosCounter.objects.filter(user_id=self.user1).update(updated_at=datetime(2023, 8, 6))
        client = APIClient()
        token = self.get_token(client=client, username=self.user1.username, password="123!")
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user2.id, 'message': 'True leader'})
        UserKudosCounter.objects.filter(user_id=self.user1).update(updated_at=datetime(2023, 8, 14))

        client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user2.id, 'message': 'Thank you!'})
        UserKudosCounter.objects.filter(user_id=self.user1).update(updated_at=datetime(2023, 8, 14))

        client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user3.id})
        UserKudosCounter.objects.filter(user_id=self.user1).update(updated_at=datetime(2023, 8, 14))

        assert UserKudosCounter.objects.get(user_id=self.user1).counter == 0

        mocked_arrow_now.return_value = arrow.Arrow(2023, 8, 23)
        res = client.post("/api/kudos/", data={'from_id': self.user1.id, 'to_id': self.user3.id})
        assert res.status_code == 201
        assert UserKudosCounter.objects.get(user_id=self.user1).counter == 2
