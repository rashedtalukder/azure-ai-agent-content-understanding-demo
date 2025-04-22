import asyncio
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects.aio import AIProjectClient
from content_understanding.content_understanding_client import AzureContentUnderstandingClient


class AzureCredentialManager:
    async def __aenter__(self):
        self.cred = DefaultAzureCredential()
        return self.cred

    async def __aexit__(self, exc_type, exc, tb):
        await self.cred.close()


class ContentUnderstandingManager:
    def __init__(self, endpoint, api_version, cred):
        self.endpoint = endpoint
        self.api_version = api_version
        self.cred = cred

    async def __aenter__(self):
        token_provider = get_bearer_token_provider(
            self.cred, "https://cognitiveservices.azure.com/.default")
        self.client = await AzureContentUnderstandingClient.create(
            endpoint=self.endpoint,
            api_version=self.api_version,
            token_provider=token_provider
        )
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        # no explicit close on CU client, but could clean up
        pass


class ProjectClientManager:
    def __init__(self, cred, conn_str):
        self.cred = cred
        self.conn_str = conn_str

    async def __aenter__(self):
        self.client = AIProjectClient.from_connection_string(
            credential=self.cred, conn_str=self.conn_str)
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.close()
