import express, { Request, Response, Application } from "express";
import cors from "cors";

import { videoRouter } from "./routes/video";
import { channelRouter } from "./routes/channel";

export const app: Application = express();

// middleware
app.use(express.json());
app.use(cors());

// routes
app.use("/api", videoRouter);
app.use("/api", channelRouter);

app.get("/", (req: Request, res: Response) => {
  res.status(404).send("Prefix API routes with '/api'");
});
