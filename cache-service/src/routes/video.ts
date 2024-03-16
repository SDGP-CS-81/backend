import { Router } from "express";
import { getVideo, createVideo } from "../controllers/videoController";

export const videoRouter = Router();

videoRouter
  .route("/video/:videoid")
  .get(getVideo, createVideo)
  .post(createVideo);
