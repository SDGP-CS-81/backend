from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from .controllers import classify

app = FastAPI()


# default route
@app.get("/")
def root_route():
    return {"error": "Use GET /video-analysis instead"}


@app.get("/video-analysis")
async def video_analysis_route(video_id: str):
    # category_scores = await classify()# pass in image
    category_scores = "dummy data"
    frame_scores = {"detailScore": 444}
    print("video_id:", video_id)
    return {"categoryScores": category_scores, "frameScores": frame_scores}


# pip install -r requirements.txt
# uvicorn src.main:app --reload
# then in a new terminal
# curl -X POST "http://127.0.0.1:8000/prediction/" -H  "accept: application/json" -H  "Content-Type: multipart/form-data" -F "file=@image.jpg"
