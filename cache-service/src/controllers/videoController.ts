import { NextFunction, Request, Response } from "express";
import {
  FrameScores,
  ImageScores,
  Video,
  VideoDocument,
} from "../models/Video";
import axios from "axios";
import Logger from "../logger";

type TextScores = {
  imageScores: ImageScores;
  frameScores: FrameScores;
  isYtCategorized: boolean;
  textScores: { [key: string]: number };
};

// if video is not found in DB, obtain from classification and save to DB
export const getVideo = async (
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  try {
    const videoID = req.params.videoid;
    const video: VideoDocument | null = await Video.findById(videoID);

    // get video info from model and analysis
    const params: { [key: string]: string } = { video_id: videoID };

    // add category keywords if they exist
    if (req.query.categoryKeywords) {
      params["category_keywords"] = req.query.categoryKeywords.toString();
    }

    Logger.debug("Attempting to get text scores from analyser");
    const textScores: TextScores = (
      await axios.get(
        `${process.env.VIDEO_ANALYSIS_SERVICE_URI as string}/text-analysis`,
        { params },
      )
    ).data;
    Logger.debug("Text scores received from analysis service");
    Logger.debug(textScores);

    Logger.debug("Checking if video is in db");
    if (video) {
      Logger.debug("Video found in db");
      Logger.debug(video);

      return res.json({
        _id: video._id,
        imageScores: video.imageScores,
        frameScores: video.frameScores,
        textScores: textScores.textScores,
      });
    }
    Logger.debug("Video not found in db");

    let videoScores;

    if (textScores.isYtCategorized) {
      Logger.debug("Video is categorized by YT, skipping frame analysis");

      videoScores = {
        imageScores: textScores.imageScores,
        frameScores: textScores.frameScores,
      };
    } else {
      Logger.debug("Attempting to classify video from analysis service");

      videoScores = (
        await axios.get(
          `${process.env.VIDEO_ANALYSIS_SERVICE_URI as string}/video-analysis`,
          { params },
        )
      ).data;

      Logger.debug("Frame scores received from analysis service");
      Logger.debug(videoScores);
    }

    res.locals.videoID = videoID;
    res.locals.imageScores = videoScores.imageScores;
    res.locals.frameScores = videoScores.frameScores;
    res.locals.textScores = textScores.textScores;
    next();
  } catch (e: any) {
    Logger.error(`Unable to analyse video: ${e.message}`);
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
  } catch (err: any) {
    Logger.error(`Unable to create video: ${err.message}`);
    res.status(500).json({ error: "Unable to create video" });
  }
};
