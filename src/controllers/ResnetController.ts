import Resnet from "../models/Resnet";
import fs from "fs";

export default function ResnetController() {
  const resnet = new Resnet("http://localhost:5000/model/model_json/model.json");
  (async () => {
    console.log("ResnetController: Loading model...");
    await resnet.load();
    console.log("ResnetController: Model loaded");
  })();

  return {
    async predict(req: any, res: any) {
      console.log("ResnetController predict");
      
      const image = fs.readFileSync('food.jpg') //image for testing
      console.log("ResnetController image loaded");

      const input_vector = resnet.preprocess(image);
      const output = resnet.predict(input_vector);
      res.send(output);
    },
  };
}
