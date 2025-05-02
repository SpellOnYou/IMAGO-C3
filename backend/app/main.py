from fastapi import FastAPI, Query, HTTPException
from .elastic import search_photos

app = FastAPI()

@app.get("/photos/")
async def get_photos(
    title: str = Query("", description="Search title"),
    bildnummer: str = Query("", description="Search bildnummer"),
    description: str = Query("", description="Search description"),
    suchtext: str = Query("", description="Search text"),
    date_from: str = Query("", description="Date from (yyyy-mm-dd)"),
    date_to: str = Query("", description="Date to (yyyy-mm-dd)"),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(20, description="Items per page", ge=1, le=100)
):
    try:
        results = await search_photos(title, bildnummer, description, suchtext, date_from, date_to, page, page_size)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
