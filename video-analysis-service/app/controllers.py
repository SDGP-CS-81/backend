import numpy as np
from PIL import Image
import sys
from fastapi import HTTPException
from .constants import classNames
from tensorflow.keras.models import load_model

filepath = "./model/model.h5"
model = load_model(filepath, compile=True)


async def classify():
    # file = 'image.jpg'
    # if file.content_type.startswith('image/') is False:
    #   raise HTTPException(status_code=400, detail=f'File \'{file.filename}\' is not an image.')

    try:
        # rewrite this step
        # contents = await file.read()
        # pil_image = Image.open(io.BytesIO(contents))

        pil_image = pil_image.resize((224, 224))

        numpy_image = np.array(pil_image).reshape((224, 224, 3))

        prediction_array = np.array([numpy_image])
        prediction_batch = model.predict(prediction_array)
        prediction = prediction_batch[0]
        # predicted_class = np.argmax(prediction)
        category_scores = {
            class_name: score for class_name, score in zip(classNames, prediction)
        }
        return category_scores

    except:
        e = sys.exc_info()[1]
        raise HTTPException(status_code=500, detail=str(e))
