import { NextFunction, Request, Response } from "express";
import { Video, VideoDocument } from "../models/Video";
import axios from "axios";

type VideoScores = Omit<VideoDocument, "_id">;

// if video is not found in DB, obtain from classification and save to DB
export const getVideo = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const videoID = req.params.videoid;
  const video = await Video.findById(videoID);

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
  res.locals.imageScores = videoScores.imageScores;
  res.locals.frameScores = videoScores.frameScores;
  res.locals.textScores = videoScores.textScores;
  next();
};

export const createVideo = async (req: Request, res: Response) => {
  let data = req.body;

  if (res.locals.videoID)
    data = {
      _id: res.locals.videoID,
      imageScores: res.locals.imageScores,
      frameScores: res.locals.frameScores,
      textScores: res.locals.textScores,
    };

  const newVideo = await Video.create(data);

  res.json(newVideo);
};

export const updateVideo = async (req: Request, res: Response) => {
  const video = await Video.findById(req.params.videoid);

  if (!video) return res.status(204).json({ message: "Video not found" });

  const response = await Video.updateOne(
    { _id: req.params.videoid },
    new Video({
      ...video,
      ...req.body,
    })
  );
  res.json(response);
};

// returns null if nothing is found and deleted, return the deleted video if found
export const deleteVideo = async (req: Request, res: Response) => {
  const video = await Video.findByIdAndDelete(req.params.videoid);
  res.json(video);
};
