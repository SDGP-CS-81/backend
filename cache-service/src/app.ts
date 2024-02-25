import express, { Request, Response, Application } from "express";
import cors from "cors";
import { vidInfoRouter } from "./routes/vidInfo";

export const app: Application = express();

// middleware
app.use(express.json());
app.use(cors());

// routes
app.use("/api", vidInfoRouter);

app.get("/", (req: Request, res: Response) => {
  res.status(404).send("Prefix API routes with '/api'");
});
