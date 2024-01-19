import { app } from "./app";
import mongoose from "mongoose";
import dotenv from "dotenv";
dotenv.config();

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
