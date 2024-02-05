import * as tf from "@tensorflow/tfjs-node";
import { NodeFileSystem } from "@tensorflow/tfjs-node/dist/io/file_system";

class ModelWrapper {
  private model!: tf.GraphModel;
  private modelFile: NodeFileSystem;

  // rename
  private static classNames = [
    "food",
    "lowGraphics",
    "lowLight",
    "nature",
    "person",
    "sports",
    "textHeavy",
    "news",
  ];
  private static modelPath = "model/model.json";
  private static instance: ModelWrapper;

  private constructor(modelPath: string) {
    this.modelFile = tf.io.fileSystem(modelPath);
  }

  static async getInstance() {
    let instance = ModelWrapper.instance;

    if (!instance) {
      ModelWrapper.instance = new ModelWrapper(ModelWrapper.modelPath);
      instance = ModelWrapper.instance;
    }

    if (instance.model) {
      return instance;
    }

    instance.model = await tf.loadGraphModel(instance.modelFile);

    return instance;
  }

  static preprocess(image: Buffer) {
    let tensor = tf.node.decodeImage(image, 3);

    // Cast the tensor to float32
    tensor = tf.cast(tensor, "float32");

    // Resize the image to the expected size for your model
    const resized = tf.image.resizeBilinear(tensor, [224, 224]);

    // Reshape to a single-element batch so we can pass it to predict.
    const batched = tf.expandDims(resized, 0);

    return batched;
  }

  predict(input_vector: tf.Tensor<tf.Rank>) {
    const output = this.model.predict(input_vector) as tf.Tensor<tf.Rank>;
    const classWeights = Array.from(output.dataSync()).map((weight, index) => [
      ModelWrapper.classNames[index],
      weight,
    ]);

    console.log(classWeights);
    return Object.fromEntries(classWeights);
  }
}

export default ModelWrapper;
