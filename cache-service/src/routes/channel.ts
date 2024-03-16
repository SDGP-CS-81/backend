import { Router } from "express";
import { getHighestVoteForChannel, incrementVoteCount } from "../controllers/channelController";

export const channelRouter = Router();

channelRouter.route("/channel/vote-category/:channelId")
  .post(incrementVoteCount)
  .get(getHighestVoteForChannel);
