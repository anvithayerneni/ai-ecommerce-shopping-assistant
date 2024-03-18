import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from dotenv import load_dotenv


load_dotenv()

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
api_key = os.environ["AZURE_SEARCH_API_KEY"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]

client = SearchIndexClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key),
)


fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
        sortable=True,
    ),
    SearchField(
        name="external_id",
        type=SearchFieldDataType.String,
        searchable=False,
        filterable=True,
    ),
    SearchField(
        name="name",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="description",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="brand",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        facetable=True,
    ),
    SearchField(
        name="category",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        facetable=True,
    ),
    SearchField(
        name="subcategory",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        facetable=True,
    ),
    SimpleField(
        name="price",
        type=SearchFieldDataType.Double,
        filterable=True,
        sortable=True,
    ),
    SimpleField(
        name="rating",
        type=SearchFieldDataType.Double,
        filterable=True,
        sortable=True,
    ),
    SimpleField(
        name="stock",
        type=SearchFieldDataType.Int32,
        filterable=True,
        sortable=True,
    ),
    SearchField(
        name="tags",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="features",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="target_audience",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="use_cases",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="color",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        facetable=True,
    ),
    SearchField(
        name="material",
        type=SearchFieldDataType.String,
        searchable=True,
        filterable=True,
        facetable=True,
    ),
    SearchField(
        name="search_text",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(
            SearchFieldDataType.Single
        ),
        searchable=True,
        vector_search_dimensions=384,
        vector_search_profile_name="product-vector-profile",
    ),
]


vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="product-hnsw",
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="product-vector-profile",
            algorithm_configuration_name="product-hnsw",
        )
    ],
)


index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
)


result = client.create_or_update_index(index)

print(f"Created/updated index: {result.name}")
print(f"Vector dimensions: 384")