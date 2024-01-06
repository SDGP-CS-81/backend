import { Router } from "express";
import {
  getVidInfo,
  setVidInfo,
  updateVidInfo,
  deleteVidInfo,
} from "../controllers/vidInfoController";
export const vidInfoRouter = Router();

vidInfoRouter
  .route("/vidInfo")
  .get(getVidInfo)
  .post(setVidInfo)
  .put(updateVidInfo)
  .delete(deleteVidInfo);
