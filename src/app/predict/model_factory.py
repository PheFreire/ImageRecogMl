from numpy.typing import NDArray
from simple_duck_ml import Model
import numpy as np
import os

ROOT = os.getenv("ROOT", os.getcwd())
MODEL_NAME = os.getenv("MODEL_NAME", "duck")
MODELS_PATH = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODELS_PATH, MODEL_NAME)

model = Model.load(MODEL_PATH)

def predict(img: NDArray[np.float64]):
    classes = ["ice_cream", "crab"]

    pred = model.forward(img)
    predicted = classes[int(np.argmax(pred))]
    
    output = {classes[n]: f"{(float(pred[n])*100):.2f}%" for n in range(0, len(classes)) }

    return { "predicted": predicted,  "output": output }

