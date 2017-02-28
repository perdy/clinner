import json
from enum import Enum

import requests

from clinner.exceptions import WrongResourceError

__all__ = ['Client', 'Resource']


class Resource(Enum):
    login = '/v1/auth/app-id/login'
    secret = '/v1/secret'


class Client:
    def __init__(self, vault, app_id=None, user_id=None):
        """
        Instantiates the vault client on the given Vault endpoint. If app_id and user_id are provided,
        login request is automatically performed, and the token is set.

        :param vault: vault url
        """
        self.vault = vault

        if app_id and user_id:
            self.app_id = app_id
            self.user_id = user_id

            self.token = self.login(app_id, user_id)
        else:
            self.token = None

    def _url(self, resource):
        """
        Create url for given resource.

        :param resource: Resource.
        :return: Vault url.
        """
        try:
            return 'https://{}{}'.format(self.vault, Resource[resource.name].value)
        except KeyError:
            raise WrongResourceError(resource)

    @property
    def connected(self):
        """
        Check if logged in.

        :return: True if already logged in.
        """
        return self.token is not None

    def login(self, app_id, user_id):
        """
        Login with the given app_id and user_id into the Vault API. This call sets the auth token on the client.

        :param app_id: app id
        :param user_id: user id
        :return: auth token
        """
        headers = {'Content-type': 'application/json'}
        body = {'app_id': app_id, 'user_id': user_id}
        url = self._url(Resource.LOGIN)

        res = requests.post(url, data=json.dumps(body), headers=headers)
        res.raise_for_status()

        return res.json()['auth']['client_token']

    def get_secret(self, secret_path):
        """
        Retrieve secret from Vault on given path.

        :param secret_path: path to the secret
        :return: dictionary of secret(s)
        """
        headers = {'X-Vault-Token': self.token}
        url = '{}/{}'.format(self._url(Resource.SECRET), secret_path)

        res = requests.get(url, headers=headers)
        res.raise_for_status()

        return res.json()['data']
