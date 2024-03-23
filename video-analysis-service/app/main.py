from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Json
from app.video_analyser import VideoAnalyser
from app.video_downloader import VideoDownloader
from app.image_classifier import ImageClassifier
import asyncio
from app.logger import setup_logger

logger = setup_logger(
    __name__, log_level="DEBUG", log_file="video-analysis-service.log"
)

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
    logger.info("Received request for root route.")
    return {"error": "Use GET /video-analysis instead"}


@app.get("/text-analysis")
async def text_analysis_route(video_id: str, category_keywords: Json | None = None):
    logger.info(
        f"Received request for text analysis: video_id: {video_id}, category_keywords: {category_keywords}"
    )

    vid_dl = VideoDownloader(video_id)
    video_category, video_text_data = await vid_dl.get_video_text_info()

    merged_keywords = VideoAnalyser.merge_keywords(category_keywords)
    text_scores = VideoAnalyser.calculate_text_scores(video_text_data, merged_keywords)

    is_yt_categorized = VideoAnalyser.yt_categorization_check(
        video_category, text_scores
    )

    response_data = VideoAnalyser.generate_dummy_scores()

    response_data["isYtCategorized"] = is_yt_categorized
    response_data["textScores"] = text_scores

    logger.info("Text analysis complete, sending data")
    logger.info(response_data)

    return response_data


@app.get("/video-analysis")
async def video_analysis_route(video_id: str, category_keywords: Json | None = None):
    logger.info(
        f"Received request for video analysis: video_id: {video_id}, category_keywords: {category_keywords}"
    )

    vid_dl = VideoDownloader(video_id)

    response_data = VideoAnalyser.generate_dummy_scores()

    video_frames = await vid_dl.get_video_frames()
    connection_closing_coroutine = vid_dl.close_http_connections()
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

    await connection_closing_coroutine
    logger.info("Video analysis completed. Returning response data.")
    logger.info(response_data)
    return response_data
