import requests
from urllib.parse import urlparse
from rest_framework import exceptions

class oauth_42:
    url = 'https://api.intra.42.fr/v2/me'

    def __init__(self, token):
        self.token = token

    def me(self):
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code != 200:
            raise exceptions.AuthenticationFailed('Failed to connect to intra')
        self.json = response.json()

    def get_uid(self):
        return self.json['id']

    def get_username(self):
        return self.json['login']

    def get_first_name(self):
        return self.json['first_name']

    def get_image_url(self):
        return self.json['image']['link']

    def get_image_name(self):
        image_url = self.json['image']['link']
        return urlparse(image_url).path.split('/')[-1]

    def fetch_image(self):
        response = requests.get(self.image_url)
        if response.status_code != 200:
            raise exceptions.AuthenticationFailed('Failed to connect to intra')
        image_file = open('media/' + self.image_name, 'wb')
        image_file.write(response.content)
        image_file.close()


    def get_user(self, user):
        self.me()
        self.image_url = self.get_image_url()
        self.image_name = self.get_image_name()
        self.fetch_image()
        user.uid = int(self.get_uid())
        user.username = self.get_username()
        user.first_name = self.get_first_name()
        user.image = self.image_name
        user.save()

