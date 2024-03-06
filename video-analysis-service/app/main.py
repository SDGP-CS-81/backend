from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Json
from app.video_analyser import VideoAnalyser
from app.video_downloader import VideoDownloader
from app.image_classifier import ImageClassifier
import asyncio

app = FastAPI()
# Restrict this when we deploy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root_route():
    return {"error": "Use GET /video-analysis instead"}


@app.get("/video-analysis")
async def video_analysis_route(video_id: str, category_keywords: Json | None = None):
    vid_dl = VideoDownloader(video_id)
    video_category, video_text_data = await vid_dl.get_video_text_info()

    text_scores = (
        VideoAnalyser.calculate_text_scores(video_text_data, category_keywords)
        if category_keywords is not None
        else {}
    )

    response_data = {
        "imageScores": {key: 0 for key in ImageClassifier.CLASS_NAMES},
        "frameScores": {"detailScore": 0, "diffScore": 0},
        "textScores": text_scores,
    }

    # Hack to use YT category to boost score and exit early
    # This should be synchronized with the frontend
    if "music" in video_category[0].lower():
        text_scores["music"] = 1000
        return response_data
    elif "gaming" in video_category[0].lower():
        text_scores["gaming"] = 1000
        return response_data

    video_frames = await vid_dl.get_video_frames()
    vid_analyser = VideoAnalyser(video_frames)
    (
        detail_score,
        diff_score,
        selected_frame,
    ) = await vid_analyser.calculate_frame_scores()

    image_scores = await asyncio.to_thread(
        ImageClassifier().classify_frame, selected_frame
    )

    response_data["imageScores"] = image_scores
    response_data["frameScores"] = {
        "detailScore": detail_score,
        "diffScore": diff_score,
    }

    return response_data
