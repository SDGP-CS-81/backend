import numpy as np
import tflite_runtime.interpreter as tflite

class ImageClassifier:
    MODEL_PATH = "model/model.tflite"
    CLASS_NAMES = [
        "lowGraphics",
        "lowLight",
        "nature",
        "person",
        "sports",
        "textHeavy",
        "news",
    ]
    IMAGE_DIMENSION = (224, 224)

    @staticmethod
    async def classify_frame(frame):
        resized_frame = frame.resize(ImageClassifier.IMAGE_DIMENSION)

        numpy_image = np.array(resized_frame).reshape(
            (ImageClassifier.IMAGE_DIMENSION + (3,))
        )

        prediction_array = np.array([numpy_image])
        prediction_batch = ImageClassifier.MODEL.predict(prediction_array)
        prediction = prediction_batch[0]
        category_scores = {
            class_name: float(score)
            for class_name, score in zip(ImageClassifier.CLASS_NAMES, prediction)
        }

        return category_scores
