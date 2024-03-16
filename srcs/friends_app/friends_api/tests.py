import logging
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Friend
from user_api.models import User
from unittest.mock import MagicMock, patch
from .views import FriendDetailView
from .serializers import FriendSerializer
import re
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    # Example pattern for a test JSON file
    if re.search(r'/users', args[0]):
        return MockResponse({}, 200)

    # Another pattern example
    if re.search(r'/anothertest\.json$', args[0]):
        return MockResponse({"key2": "value2"}, 200)

    # Default response if no pattern matches
    return MockResponse(None, 404)

class FriendDetailViewTests(APITestCase):
    
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user1 = MagicMock(spec=User)
        self.user2 = MagicMock(spec=User)
        self.user3 = MagicMock(spec=User)

        self.user1.pk = 88507
        self.user1.username = 'kamin'
        self.user1.first_name = 'karim'
        self.user1.image = '/media/kamin_GI4ecJv.jpg'
        self.user1.status = 0

        self.user2.pk = 88336
        self.user2.username = 'lde-alen'
        self.user2.first_name = 'Lucas'
        self.user2.image = '/media/kamin_GI4ecJv.jpg'
        self.user2.status = 0
        
        self.user3.pk = 883367
        self.user3.username = 'lde-alen'
        self.user3.first_name = 'Lucas'
        self.user3.image = '/media/kamin_GI4ecJv.jpg'
        self.user3.status = 0

        # Create a Friend instance if needed for testing
        self.friend = Friend.objects.create(first_id=self.user1.pk, second_id=self.user2.pk, relationship=0)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_create_friend(self, mocked_requests_get):
        url = reverse('friend-detail')
        alreadyFriends1 = {
            'session_id': 'some-session-id',
            'access_token': 'some-access-token',
            'first_id': f'{self.user1.pk}',
            'second_id': f'{self.user2.pk}',
            'relationship': 1
        }
        alreadyFriends2 = {
            'session_id': 'some-session-id',
            'access_token': 'some-access-token',
            'first_id': f'{self.user2.pk}',
            'second_id': f'{self.user1.pk}',
            'relationship': 1
        }
        notFriends = {
            'session_id': 'some-session-id',
            'access_token': 'some-access-token',
            'first_id': f'{self.user1.pk}',
            'second_id': f'{self.user3.pk}',
            'relationship': 1
        }
        badRequest1 = {
            'session_id': 'some-session-id',
            'access_token': 'some-access-token',
            'first_id': f'{self.user3.pk}',
            'relationship': 1
        }
        badRequest2 = {
            'session_id': 'some-session-id',
            'access_token': 'some-access-token',
            'second_id': f'{self.user3.pk}',
            'relationship': 1
        }
        badRequest3 = {
            'access_token': 'some-access-token',
            'first_id': f'{self.user1.pk}',
            'second_id': f'{self.user3.pk}',
            'relationship': 1
        }
        badRequest4 = {
            'session_id': 'some-session-id',
            'first_id': f'{self.user1.pk}',
            'second_id': f'{self.user3.pk}',
            'relationship': 1
        }
        badRequest5 = {
            'session_id': 'some-session-id',
            'access_token': 'some-access-token',
            'first_id': f'{self.user1.pk}',
            'second_id': f'{self.user3.pk}',
        }
        response = self.client.post(url, alreadyFriends1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, alreadyFriends2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, badRequest1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, badRequest2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, badRequest3, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, badRequest4, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, badRequest5, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, notFriends, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    # def test_update_friend_relationship(self):
    #     # Similar to test_create_friend, but using self.client.put and checking for HTTP_200_OK

    # def test_delete_friend(self):
    #     # Use self.client.delete and ensure the friend instance is deleted

    # def test_get_friends_list(self):
    #     # Test the GET method when listing friends or checking friendship status
    #     # This might require mocking the external API call to get_user_info

