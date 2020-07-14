import unittest
from main import app
from io import BytesIO
from os import remove
import jwt
import json
from http import HTTPStatus


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
        with app.test_client() as client:
            rv = self.upload_file(client)
            link: str = json.loads(rv.data)["url"].split('/')[-1]
            filename = link.split('/')[-1]
            self.files.append(filename)

    def test_get_file(self):
        link = ""
        with app.test_client() as client:
            rv = self.upload_file(client)

            link: str = json.loads(rv.data)["url"].split('/')[-1]
            filename = link.split('/')[-1]
            rv = client.get('/api/filestorage/' + filename)
            self.assertEqual(rv.status_code, HTTPStatus.OK)
            self.files.append(filename)

    def test_update_file(self):
        link = ""
        with app.test_client() as client:
            rv = self.upload_file(client)
            # Get URL
            link: str = json.loads(rv.data)["url"]

            # Put file with the loaded URL
            with open('ContractWorkplaces-Logo2014.jpg', 'rb') as file_updated:
                client.environ_base['HTTP_AUTHORIZATION'] = self.build_token(self.key)
                files = {'file': (BytesIO(file_updated.read()), 'test.jpg')}
                rv = client.put(link,
                                data=files,
                                follow_redirects=True,
                                content_type='multipart/form-data')
                file_updated.close()
                self.assertEqual(rv.status_code, HTTPStatus.OK)
                self.assertEqual(json.loads(rv.data)["url"], link)

                filename = link.split('/')[-1]
                self.files.append(filename)

    def test_delete(self):
        link = ""
        with app.test_client() as client:
            rv = self.upload_file(client)
            # Get URL
            link: str = json.loads(rv.data)["url"]
            filename = link.split('/')[-1]
            # Delete file
            client.environ_base['HTTP_AUTHORIZATION'] = self.build_token(self.key)
            rv = client.delete('/api/filestorage/' + filename)
            self.assertEqual(rv.status_code, HTTPStatus.OK)

            # Get a file deleted
            rv = client.get('/api/filestorage/' + filename)
            self.assertEqual(rv.status_code, HTTPStatus.NOT_FOUND)

    def upload_file(self, client):
        with open('ContractWorkplaces-Logo2014.jpg', 'rb') as test_file:
            client.environ_base['HTTP_AUTHORIZATION'] = self.build_token(self.key)
            files = {'file': (BytesIO(test_file.read()), 'test.jpg')}

            rv = client.post('/api/filestorage/save',
                             data=files,
                             follow_redirects=True,
                             content_type='multipart/form-data')
            test_file.close()
            self.assertEqual(rv.status_code, HTTPStatus.CREATED)
            return rv

    def tearDown(self):
        for file in self.files:
            remove(file)


if __name__ == '__main__':
    unittest.main()
