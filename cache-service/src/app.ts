import express, { Request, Response, Application } from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";

import { videoRouter } from "./routes/video";
import { channelRouter } from "./routes/channel";

export const app: Application = express();

const secondsLimiter = rateLimit({
  windowMs: 1 * 1000, // 1 second time window
  max: 10,
  message: "Too many requests thrown per second, please try again later.",
});

const minuteLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute time window
  max: 100, // maximum 100 requests per window
  message: "Too many requests thrown per minute, please try again later.",
});

// middleware
app.use(secondsLimiter, minuteLimiter);
app.use(express.json());
app.use(cors());

// Apply the rate limiter to the routes
app.use("/api", videoRouter);
app.use("/api", channelRouter);

app.get("/", (req: Request, res: Response) => {
  res.status(404).send("Prefix API routes with '/api'");
});
