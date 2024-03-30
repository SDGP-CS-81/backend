import { Request, Response } from "express";
import { Video } from "../models/Video";
import axios from "axios";
import Logger from "../logger";

type VideoScores = {
  isYtCategorized: boolean;
  textScores: { [key: string]: number };
};

// if video is not found in DB, obtain from classification and save to DB
export const getVideo = async (req: Request, res: Response) => {
  try {
    const videoID = req.params.videoid;
    // const video: VideoDocument | null = await Video.findById(videoID);

    // get video info from model and analysis
    const params: { [key: string]: string } = { video_id: videoID };

    // add category keywords if they exist
    if (req.query.categoryKeywords) {
      params["category_keywords"] = req.query.categoryKeywords.toString();
    }

    Logger.debug("Attempting to get text scores from analyser");
    const textScores: VideoScores = (
      await axios.get(
        `${process.env.VIDEO_ANALYSIS_SERVICE_URI as string}/video-analysis`,
        { params }
      )
    ).data;
    Logger.debug("Text scores received from analysis service");
    Logger.debug(textScores);

    return res.json({
      _id: videoID,
      textScores: textScores.textScores,
    });
  } catch (error) {
    Logger.error(
      `Unable to analyse video: ${error instanceof Error ? error.message : ""}`
    );
    res.status(500).json({ error: "Unable to analyse video" });
  }
};

export const createVideo = async (req: Request, res: Response) => {
  try {
    let data = req.body;

    if (res.locals.videoID)
      data = {
        _id: res.locals.videoID,
        imageScores: res.locals.imageScores,
        frameScores: res.locals.frameScores,
      };

    Logger.debug("Caching video frame scores in db");
    Video.create(data);

    const textScores = res.locals.textScores;

    res.json({ ...data, textScores });
  } catch (error) {
    Logger.error(
      `Unable to create video: ${error instanceof Error ? error.message : ""}`
    );
    res.status(500).json({ error: "Unable to create video" });
  }
};
