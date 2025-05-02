from elasticsearch import AsyncElasticsearch
import logging
from .config import ELASTICSEARCH_CONFIG

# Configure logging
logger = logging.getLogger(__name__)

es = AsyncElasticsearch(
    **ELASTICSEARCH_CONFIG
    )

async def search_photos(title: str = "", bildnummer: str = "", description: str = "", suchtext: str = "", date_from: str = "", date_to: str = "", page: int = 1, page_size: int = 20):
    logger.info(f"Searching photos with parameters: title={title}, bildnummer={bildnummer}, description={description}, suchtext={suchtext}, date_from={date_from}, date_to={date_to}, page={page}, page_size={page_size}")
    
    must_clauses = [] # all given clauses should match

    if title:
        must_clauses.append({
            "match": {
                "title": title
            }
        })
    
    if bildnummer:
        must_clauses.append({
            "term": {
                "bildnummer": {
                    "value": bildnummer
                }
            }
        })
    
    if description:
        must_clauses.append({
            "match": {
                "description": description
            }
        })

    if suchtext:
        must_clauses.append({
            "match": {
                "suchtext": suchtext
            }
        })

    if date_from or date_to:
        range_query = {}
        if date_from:
            range_query["gte"] = date_from
        if date_to:
            range_query["lte"] = date_to
        must_clauses.append({
            "range": {
                "datum": range_query
            }
        })

    # Calculate the from parameter for pagination
    from_param = (page - 1) * page_size

    query_body = {
        "query": {
            "bool": {
                "must": must_clauses
            }
        },
        "from": from_param,
        "size": page_size
    }

    try:
        logger.debug(f"Executing Elasticsearch query: {query_body}")
        response = await es.search(index="imago", body=query_body)
        hits = response['hits']['hits']
        total_hits = response['hits']['total']['value']
        logger.info(f"Search completed. Found {total_hits} total hits, returning {len(hits)} results")

        photos = []
        for hit in hits:
            src = hit["_source"]
            photo = {
                "id": hit["_id"],
                "mediaId": src.get("bildnummer", ""),
                "description": src.get("description", ""),
                "title": src.get("title", ""),
                "searchText": src.get("suchtext", ""),
                "date": src.get("datum", ""),
                "width": src.get("breite", ""),
                "height": src.get("hoehe", ""),
                "db": src.get("db", ""),
            }
            photos.append(photo)
        
        return {
            "photos": photos,
            "total": total_hits,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_hits + page_size - 1) // page_size
        }
    except Exception as e:
        logger.error(f"Error executing Elasticsearch query: {str(e)}", exc_info=True)
        raise
