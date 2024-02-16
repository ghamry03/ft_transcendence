import requests
from urllib.parse import urlparse
from rest_framework import exceptions
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

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
            response = requests.get('http://localhost:3000/media/johndoe.png')
        #     raise exceptions.AuthenticationFailed('Failed to connect to intra')

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()
        return img_temp


    def create_user(self, new_user):
        self.me()

        new_user.uid = int(self.get_uid())
        new_user.username = self.get_username()
        new_user.first_name = self.get_first_name()

        new_user.validate_unique()

        self.image_url = self.get_image_url()
        self.image_name = self.get_image_name()
        tmp_img = self.fetch_image()

        new_user.image.save(
            self.image_name,
            File(tmp_img),
            save=True
        )
