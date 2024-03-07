import { Router } from "express";
import { incrementVoteCount } from "../controllers/channelController";

export const channelRouter = Router();

channelRouter.route("/channel/vote-category").post(incrementVoteCount);
