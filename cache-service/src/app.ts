import express, { Request, Response, Application } from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";

import { videoRouter } from "./routes/video";
import { channelRouter } from "./routes/channel";

export const app: Application = express();

// middleware
app.use(express.json());
app.use(cors());

const limiter = rateLimit({
  windowMs: 5 * 60 * 1000, // 5 minute
  max: 300, //maximum 300 requests per 5 minutes
  message: "Too many requests, please try again later.",
});

// Apply the rate limiter to the routes
app.use("/api", limiter, videoRouter);
app.use("/api", limiter, channelRouter);

app.get("/", (req: Request, res: Response) => {
  res.status(404).send("Prefix API routes with '/api'");
});
