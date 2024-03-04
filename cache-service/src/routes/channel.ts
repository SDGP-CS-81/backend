import { Router } from "express";
import { incrementVoteCount } from "../controllers/channelController";

export const channelRouter = Router();

channelRouter.route("/save-info").post(incrementVoteCount);
