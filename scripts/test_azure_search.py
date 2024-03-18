import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv


load_dotenv()

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
api_key = os.environ["AZURE_SEARCH_API_KEY"]

client = SearchIndexClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key),
)

print("Connected to Azure AI Search")
print(f"Endpoint: {endpoint}")

indexes = list(client.list_indexes())

print(f"Existing indexes: {len(indexes)}")

for index in indexes:
    print(f"- {index.name}")