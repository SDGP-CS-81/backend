import * as tf from "@tensorflow/tfjs-node";


class Resnet {
  model!: tf.GraphModel
  modelUrl: string;

  constructor(modelUrl: string) {
    this.modelUrl = modelUrl;
  }

  async load() {
    console.log("Resnet load");
    this.model = await tf.loadGraphModel (this.modelUrl);
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
    return Array.from(output.dataSync()); //comment this to see the class index
    const predictions = tf.argMax(output, 1);
    return Array.from(predictions.dataSync());
  }
}

export default Resnet;