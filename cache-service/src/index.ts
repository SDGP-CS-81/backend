import { app } from "./app";
import mongoose from "mongoose";
import dotenv from "dotenv";
dotenv.config();

app.listen(5000);

mongoose.connect(process.env.MONGODB_URI!).then(() => {
  console.log("Connected to Database Successfully");
});
