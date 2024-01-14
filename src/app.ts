import express, { Request, Response, Application } from "express";
import dotenv from "dotenv";
dotenv.config();
import mongoose from "mongoose";
import cors from "cors";
import { vidInfoRouter } from "./routes/vidInfo";
const app: Application = express();

// middleware
app.use(express.json());
app.use(cors());

// routes
app.use("/api", vidInfoRouter);

app.get("/", (req: Request, res: Response) => {
  res.send("Hello world");
});

app.listen(5000, () => {
  console.log("Server is running on port 5000");
});

mongoose
  .connect(process.env.MONGO_URI!)
  .then(() => {
    console.log("Connected to MongoDB Successfully");
  })
  .catch((err) => {
    console.log(err);
  });
