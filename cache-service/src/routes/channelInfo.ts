import { Router } from 'express';
import { incrementVoteCount } from "../controllers/channelInfoController";

export const channelInfoRouter = Router();

channelInfoRouter.route("/save-info")
  .post(incrementVoteCount);