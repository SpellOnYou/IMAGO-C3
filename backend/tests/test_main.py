from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
from elasticsearch import AsyncElasticsearch
import warnings

client = TestClient(app)

@pytest.fixture(autouse=True)
def suppress_elasticsearch_warnings():
    """Suppress Elasticsearch warnings during tests"""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=Warning)
        warnings.filterwarnings("ignore", module="elasticsearch")
        yield

@pytest.fixture(autouse=True)
def mock_elasticsearch():
    """Mock the Elasticsearch client for all tests"""
    # Create a fresh mock for each test
    mock_es = AsyncMock(spec=AsyncElasticsearch)
    
    # Set up the mock to handle async calls
    mock_es.search = AsyncMock(return_value={
        'hits': {
            'hits': [],
            'total': {'value': 0}
        }
    })
    mock_es.__aenter__ = AsyncMock(return_value=mock_es)
    mock_es.__aexit__ = AsyncMock(return_value=None)
    
    # Mock the client and transport
    with patch('elasticsearch.AsyncElasticsearch', return_value=mock_es) as mock_es_class:
        mock_es_class._transport_class = MagicMock()
        mock_es_class._transport_class.DEFAULT = {
            'hosts': ['http://localhost:9200'],
            'verify_certs': True,
            'ssl_show_warn': False,
            'use_ssl': False
        }
        with patch('app.elastic.es', mock_es):
            yield mock_es

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def test_get_photos_basic(mock_elasticsearch):
    """Test basic photo search without parameters"""
    response = client.get("/photos/")
    assert response.status_code == 200
    data = response.json()
    assert all(key in data for key in ["photos", "total", "page", "page_size", "total_pages"])

@pytest.mark.parametrize("search_params", [
    {"title": "test"},
    {"bildnummer": "12345"},
    {"description": "test description"},
    {"suchtext": "test search"},
    {"date_from": "2020-01-01", "date_to": "2020-12-31"},
    {"page": 2, "page_size": 10}
])
def test_get_photos_with_parameters(mock_elasticsearch, search_params):
    """Test photo search with different parameters"""
    response = client.get("/photos/", params=search_params)
    assert response.status_code == 200
    data = response.json()
    assert "photos" in data
    assert isinstance(data["photos"], list)

def test_get_photos_pagination(mock_elasticsearch):
    """Test pagination functionality"""
    # Mock paginated responses
    async def paginated_search(*args, **kwargs):
        page = (kwargs.get('body', {}).get('from', 0) // 5) + 1
        hits = [{'_id': str(i), '_source': {'title': f'Photo {i}'}} 
                for i in range(5*(page-1), 5*page)]
        return {'hits': {'hits': hits, 'total': {'value': 10}}}
    
    mock_elasticsearch.search = AsyncMock(side_effect=paginated_search)
    
    # Test pages
    for page in [1, 2]:
        response = client.get("/photos/", params={"page": page, "page_size": 5})
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == page
        assert len(data["photos"]) == 5

def test_get_photos_invalid_page(mock_elasticsearch):
    """Test invalid page number handling"""
    response = client.get("/photos/", params={"page": 0, "page_size": 10})
    assert response.status_code == 422

def test_get_photos_invalid_page_size(mock_elasticsearch):
    """Test invalid page size handling"""
    response = client.get("/photos/", params={"page": 1, "page_size": 0})
    assert response.status_code == 422

def test_get_photos_error_handling(mock_elasticsearch):
    """Test error handling when Elasticsearch fails"""
    mock_elasticsearch.search = AsyncMock(side_effect=Exception("Search failed"))
    response = client.get("/photos/")
    assert response.status_code == 500
    assert "detail" in response.json()

def test_get_photos_response_structure(mock_elasticsearch):
    """Test the structure of the photo response"""
    mock_elasticsearch.search = AsyncMock(return_value={
        'hits': {
            'hits': [{
                '_id': '1',
                '_source': {
                    'bildnummer': 'test1',
                    'description': 'test description',
                    'title': 'test title',
                    'suchtext': 'test search text',
                    'datum': '2020-01-01',
                    'breite': 100,
                    'hoehe': 100,
                    'db': 'test'
                }
            }],
            'total': {'value': 1}
        }
    })
    
    response = client.get("/photos/")
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert all(key in data for key in ["photos", "total", "page", "page_size", "total_pages"])
    if data["photos"]:
        photo = data["photos"][0]
        assert all(key in photo for key in [
            "id", "mediaId", "description", "title", 
            "searchText", "date", "width", "height", "db"
        ])
