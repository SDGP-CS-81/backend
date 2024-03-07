import { Router } from "express";
import {
  getVideo,
  createVideo,
  updateVideo,
  deleteVideo,
} from "../controllers/videoController";

export const videoRouter = Router();

videoRouter
  .route("/video/:videoid")
  .get(getVideo)
  .put(updateVideo)
  .delete(deleteVideo);

videoRouter
  .route("/video")
  .post(createVideo);
