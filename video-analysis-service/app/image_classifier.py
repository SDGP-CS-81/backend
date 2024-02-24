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

    __instance = None
    def __new__(cls):
        if (cls.__instance is None):
            cls.__instance = super(ImageClassifier,cls).__new__(cls)

        return cls.__instance
    
    def __init__(self):
        if (self.__instance is not None):
            self._interpreter = tflite.Interpreter(model_path=ImageClassifier.MODEL_PATH)
            self._interpreter.allocate_tensors()

            self._input_details = self._interpreter.get_input_details()[0]
            self._output_details = self._interpreter.get_output_details()[0]
            
    async def classify_frame(self,frame):

        resized_frame = frame.resize(ImageClassifier.IMAGE_DIMENSION)
        numpy_image = np.array(resized_frame).reshape(
            (ImageClassifier.IMAGE_DIMENSION + (3,))
        )
        
        prediction_array = np.expand_dims(numpy_image, axis=0).astype(self._input_details["dtype"])
        self._interpreter.set_tensor(self._input_details["index"], prediction_array)
        self._interpreter.invoke()
        prediction = self._interpreter.get_tensor(self._output_details["index"])[0]

        category_scores = {
            class_name: float(score)
            for class_name, score in zip(ImageClassifier.CLASS_NAMES, prediction)
        }

        return category_scores
