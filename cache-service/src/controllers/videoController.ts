import { NextFunction, Request, Response } from "express";
import { VideoModel } from "../models/Video";
import axios from "axios";

type VideoScores = {
  categoryScores: { [key: string]: number };
  frameScores: { [key: string]: number };
  keywordScores: { [key: string]: number };
};

// if video is not found in DB, obtain from classification and save to DB
export const getVideo = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const videoID = req.params.videoid;
  const video = await VideoModel.findById(videoID);

  if (video && !video.categoryScores) {
    // if video is found in DB, but has no categoryProbabilities, only userRated,
    // then get categoryProbabilities from classification and save to DB
    return res.json(video);
  }

  if (video) return res.json(video);

  // get video info from model and analysis
  const params: { [key: string]: string } = { video_id: videoID };

  // add category keywords if they exist
  if (req.query.categoryKeywords) {
    params["category_keywords"] = req.query.categoryKeywords.toString();
  }

  const videoScores: VideoScores = (
    await axios.get(
      `${process.env.VIDEO_ANALYSIS_SERVICE_URI as string}/video-analysis`,
      { params }
    )
  ).data;

  res.locals.videoID = videoID;
  res.locals.categoryScores = videoScores.categoryScores;
  res.locals.frameScores = videoScores.frameScores;
  res.locals.keywordScores = videoScores.keywordScores;
  next();
};

export const createVideo = async (req: Request, res: Response) => {
  let data = req.body;

  if (res.locals.videoID)
    data = {
      _id: res.locals.videoID,
      categoryScores: res.locals.categoryScores,
      frameScores: res.locals.frameScores,
      keywordScores: res.locals.keywordScores,
    };

  const newVideo = await VideoModel.create(data);

  res.json(newVideo);
};

export const updateVideo = async (req: Request, res: Response) => {
  const video = await VideoModel.findById(req.params.videoid);

  if (!video) return res.status(204).json({ message: "Video not found" });

  const response = await VideoModel.updateOne(
    { _id: req.params.videoid },
    new VideoModel({
      ...video,
      ...req.body,
    })
  );
  res.json(response);
};

// returns null if nothing is found and deleted, return the deleted video if found
export const deleteVideo = async (req: Request, res: Response) => {
  const video = await VideoModel.findByIdAndDelete(req.params.videoid);
  res.json(video);
};
