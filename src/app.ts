// import express, { Request, Response, Application } from "express";
// import cors from "cors";
// import { vidInfoRouter } from "./routes/vidInfo";

// export const app: Application = express();

// // middleware
// app.use(express.json());
// app.use(cors());

// // routes
// app.use("/api", vidInfoRouter);

// app.get("/", (req: Request, res: Response) => {
//   res.send("Hello world");
// });

import express, { Request, Response, Application } from "express";
import cors from "cors";
import { vidInfoRouter } from "./routes/vidInfo";
import ResnetController from "./controllers/ResnetController";

export const app: Application = express();

const resnetcontroller = ResnetController()

// middleware
app.use(express.json());
app.use(cors());

// routes
app.use("/api", vidInfoRouter);

app.use("/model", express.static("model"));

app.get("/predict", resnetcontroller.predict)

app.get("/", (req: Request, res: Response) => {
  res.send("Hello world");
});

//http://localhost:5000/predict