from numpy.typing import NDArray
from simple_duck_ml import Model
import numpy as np
import os

from app.utils.show_img import show_img

ROOT = os.getenv("ROOT", os.getcwd())
MODEL_NAME = os.getenv("MODEL_NAME", "duck")
MODELS_PATH = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODELS_PATH, MODEL_NAME)

print(f"CWD = \"{os.getcwd()}\"")

for key, path in {"ROOT": ROOT, "MODEL_NAME": MODEL_NAME, "MODELS_PATH": MODELS_PATH, "MODEL_PATH": MODEL_PATH, }.items():
    print(f"{key} = \"{path}\" exists = {os.path.exists(path)}")
    print(f"[LIST DIR: {path}]")
    if os.path.exists(path):
        for dir in os.listdir(path):
            print(dir)
    print("-="*15)


def get_labels():
    envs = os.getenv("LOADED_LABELS", "").split("|")
    return [label.strip() for label in envs]

def predict(img: NDArray[np.float64]):
    model = Model.load(MODEL_PATH)
    classes = get_labels()
    
    pred = model.forward(img)
    predicted = classes[int(np.argmax(pred))]
    
    output = {classes[n]: f"{(float(pred[n])*100):.2f}%" for n in range(0, len(classes)) }

    return { "predicted": predicted,  "output": output }

