import express, { Request, Response, Application } from "express";
import cors from "cors";
import { vidInfoRouter } from "./routes/vidInfo";
import { channelInfoRouter } from "./routes/channelInfo";

export const app: Application = express();

// middleware
app.use(express.json());
app.use(cors());

// routes
app.use("/api", vidInfoRouter);
app.use("/api/channel", channelInfoRouter);

app.get("/", (req: Request, res: Response) => {
  res.send("Hello world");
});
