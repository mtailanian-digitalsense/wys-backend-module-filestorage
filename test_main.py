import unittest
from unittest import TestCase

from main import app
from io import BytesIO
from os import remove
import jwt
import json


class FileStorageSave(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.files = []
        f = open('oauth-private.key', 'r')
        self.key = f.read()
        f.close()

    @staticmethod
    def build_token(key, user_id=1):
        payload = {
            "aud": "1",
            "jti": "450ca670aff83b220d8fd58d9584365614fceaf210c8db2cf4754864318b5a398cf625071993680d",
            "iat": 1592309117,
            "nbf": 1592309117,
            "exp": 1624225038,
            "sub": "23",
            "user_id": user_id,
            "scopes": [],
            "uid": 23
        }
        return ('Bearer ' + jwt.encode(payload,
                                       key,
                                       algorithm='RS256')
                               .decode('utf-8')).encode('utf-8')

    def test_save_file(self):
        file_test = open('ContractWorkplaces-Logo2014.jpg', 'rb')
        with app.test_client() as client:
            client.environ_base['HTTP_AUTHORIZATION'] = self.build_token(self.key)
            files = {'file': (BytesIO(file_test.read()), 'test.jpg')}
            file_test.close()
            rv = client.post('/api/filestorage/save',
                             data=files,
                             follow_redirects=True,
                             content_type='multipart/form-data')
            self.assertEqual(rv.status_code, 200)
            link: str = json.loads(rv.data)["url"].split('/')[-1]
            filename = link.split('/')[-1]
            self.files.append(filename)

    def test_get_file(self):
        file_test = open('ContractWorkplaces-Logo2014.jpg', 'rb')
        link = ""
        with app.test_client() as client:
            client.environ_base['HTTP_AUTHORIZATION'] = self.build_token(self.key)
            files = {'file': (BytesIO(file_test.read()), 'test.jpg')}
            file_test.close()
            rv = client.post('/api/filestorage/save',
                             data=files,
                             follow_redirects=True,
                             content_type='multipart/form-data')
            self.assertEqual(rv.status_code, 200)

            link: str = json.loads(rv.data)["url"].split('/')[-1]
            filename = link.split('/')[-1]
            rv = client.get('/api/filestorage/' + filename)
            self.assertEqual(rv.status_code, 200)
            self.files.append(filename)

    def tearDown(self):
        for file in self.files:
            remove(file)


if __name__ == '__main__':
    unittest.main()
