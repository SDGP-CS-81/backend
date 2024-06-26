import numpy as np
import tflite_runtime.interpreter as tflite
from app.logger import setup_logger

logger = setup_logger(
    __name__, log_level="DEBUG", log_file="video-analysis-service.log"
)


class ImageClassifier:
    MODEL_PATH = "model/model.tflite"
    CLASS_NAMES = [
        "graphics",
        "lowLight",
        "nature",
        "news",
        "person",
        "sports",
        "textHeavy",
    ]
    IMAGE_DIMENSION = (224, 224)

    _instance = None

    # returns the static instance variable on every instantiation
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        logger.debug("Initializing ImageClassifier.")
        # check if interpreter instantiated in instance, if not set interpreter and details
        try:
            self._interpreter
        except AttributeError:
            logger.debug("Loading TFLite model.")
            # load model through interpreter api
            self._interpreter = tflite.Interpreter(
                model_path=ImageClassifier.MODEL_PATH
            )
            self._interpreter.allocate_tensors()

            # retieve details of input and output tensors to shape input image acccordingly
            self._input_details = self._interpreter.get_input_details()[0]
            self._output_details = self._interpreter.get_output_details()[0]
            logger.info("Model loaded successfully.")

    def classify_frame(self, frame):
        logger.debug("Classifying frame.")
        resized_frame = frame.resize(ImageClassifier.IMAGE_DIMENSION)
        numpy_image = np.array(resized_frame).reshape(
            (ImageClassifier.IMAGE_DIMENSION + (3,))
        )

        # shape image according to model input tensor shape and pass image as batch
        prediction_array = np.expand_dims(numpy_image, axis=0).astype(
            self._input_details["dtype"]
        )
        self._interpreter.set_tensor(self._input_details["index"], prediction_array)
        self._interpreter.invoke()
        prediction = self._interpreter.get_tensor(self._output_details["index"])[0]

        logger.debug("Generating image scores.")
        image_scores = {
            class_name: float(score)
            for class_name, score in zip(ImageClassifier.CLASS_NAMES, prediction)
        }

        logger.info(f"Image scores: {image_scores}")
        return image_scores
