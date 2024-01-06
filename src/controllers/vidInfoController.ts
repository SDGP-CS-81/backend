import { NextFunction, Request, Response } from "express";
import { VidInfoModel } from "../models/VidInfo";
import { videoAnalyserClass } from "../helpers/VideoAnalyser";

// if vidInfo is not found in DB, obtain from classification and save to DB
export const getVidInfo = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const videoID = req.params.videoid;
  const vidInfo = await VidInfoModel.findById(videoID);

  if (vidInfo && !vidInfo.categoryScores) {
    // if vidInfo is found in DB, but has no categoryProbabilities, only userRated,
    // then get categoryProbabilities from classification and save to DB
    return res.json(vidInfo);
  }

  if (vidInfo) return res.json(vidInfo);

  // get video info from model and analysis
  // retrieve image frame from user???
  const { categoryScores, frameScores } = videoAnalyserClass(videoID);
  next();
};

export const createVidInfo = async (req: Request, res: Response) => {
  const data = req.body;
  const newVidInfo = await VidInfoModel.create(data);

  res.json(newVidInfo);
};

export const updateVidInfo = async (req: Request, res: Response) => {
  res.send("Hello world");
};

// returns null if nothing is found and deleted, return the deleted vidInfo if found
export const deleteVidInfo = async (req: Request, res: Response) => {
  const vid = await VidInfoModel.findByIdAndDelete(req.params.videoid);
  res.json(vid);
};
