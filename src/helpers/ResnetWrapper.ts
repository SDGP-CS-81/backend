import * as tf from "@tensorflow/tfjs-node";
import { NodeFileSystem } from "@tensorflow/tfjs-node/dist/io/file_system";

const classNames = [
  "food",
  "lowGraphics",
  "lowLight",
  "mechanicalItems",
  "nature",
  "person",
  "sports",
  "textHeavy",
  "urban",
  "news",
];

class ResnetWrapper {
  model!: tf.GraphModel;
  modelFile: NodeFileSystem;

  constructor(modelPath: string) {
    this.modelFile = tf.io.fileSystem(modelPath);
    console.log(this.modelFile);
    tf.loadGraphModel(this.modelFile).then((model) => (this.model = model));
  }

  preprocess(image: Buffer) {
    console.log("Resnet preprocess");

    let tensor = tf.node.decodeImage(image, 3);

    // Cast the tensor to float32
    tensor = tf.cast(tensor, "float32");

    // Resize the image to the expected size for your model
    const resized = tf.image.resizeBilinear(tensor, [224, 224]);

    // Normalize the image to be between 0 and 1
    const normalized = tf.div(resized, tf.scalar(255.0));

    // Reshape to a single-element batch so we can pass it to predict.
    const batched = tf.expandDims(normalized, 0);

    return batched;
  }

  predict(input_vector: tf.Tensor<tf.Rank>) {
    console.log("Resnet predict");
    const output = this.model.predict(input_vector) as tf.Tensor<tf.Rank>;
    const classWeights = Array.from(output.dataSync()).map((weight, index) => [
      classNames[index],
      weight,
    ]);

    console.log(classWeights);
    return Object.fromEntries(classWeights);
  }
}

export default ResnetWrapper;
