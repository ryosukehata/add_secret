import os
from typing import List

from google.cloud import secretmanager


class GetSecretList:
    def __init__(self, client: secretmanager.SecretManagerServiceClient,
                 project_id: int):
        self.client = client
        self.parent = f"projects/{project_id}"

    def get(self) -> List[str]:
        """
        List all secrets in the given project.
        """

        # Build the resource name of the parent project.

        secret_list = []
        for secret in self.client.list_secrets(request={"parent": self.parent}):
            secret_list.append(secret.name)

        return secret_list


class GetSecret:
    def __init__(self, client: secretmanager.SecretManagerServiceClient):
        self.client = client

    def get(self, name: str, version='latest') -> str:
        name = f'{name}/versions/{version}'
        response = self.client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload


class AddSecretEnv:
    def __init__(self, client: secretmanager.SecretManagerServiceClient,
                 project_id: int):
        self.secretlist = GetSecretList(client, project_id)
        self.secret_value = GetSecret(client)

    def get_key_value(self, secret_path):
        key = secret_path.split('/')[-1]
        value = self.secret_value.get(secret_path)
        return key, value

    def add(self):
        for secret_path in self.secretlist.get():
            key, value = self.get_key_value(secret_path)
            os.environ[key] = value
