from random import randint
from numpy import choose
from simple_duck_ml import (
    ConvolutionalLayer,
    FlattenLayer,
    DenseLayer,
    SoftmaxActivation,
    ReLuActivation,
    CrossEntropyLoss,
    Model,
)

from app.dataset.dataset_factory import DatasetFactory
from app.predict.model_factory import get_labels
from app.utils.img_normalization import normalization
import os

from app.utils.show_img import show_img

LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.001"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5"))
EPOCHS = int(os.getenv("EPOCHS", "20"))
SAMPLES_PER_CLASS = int(os.getenv("SAMPLES_PER_CLASS", "200"))

loaded_normalization = lambda img: normalization(img, resize=64)
classes = get_labels()

datasets = DatasetFactory().load_all(classes, SAMPLES_PER_CLASS, loaded_normalization)


layers = [
    ConvolutionalLayer(
        nodes_num=4,
        kernel_shape=(5, 5, 1),
        stride=1,
        activation=ReLuActivation()
    ),
    ConvolutionalLayer(
        nodes_num=8,
        kernel_shape=(3, 3, 4),
        stride=1,
        activation=ReLuActivation()
    ),
    FlattenLayer(),
    DenseLayer(
        output_size=len(datasets),
        activation=SoftmaxActivation()
    )
]
    
model = Model(
    layers=layers,
    loss=CrossEntropyLoss(),
    learning_rate=LEARNING_RATE
)


if __name__ == '__main__':
    MODEL_NAME = os.getenv("MODEL_NAME", "duck")

    ROOT = os.getenv("ROOT", os.getcwd())
    MODELS_PATH = os.path.join(ROOT, "models")
    
    MODEL_PATH = os.path.join(MODELS_PATH, MODEL_NAME)
    # model = Model.load(MODEL_PATH)

    datasets[0].x = datasets[0].x[::-1]
    datasets[1].x = datasets[1].x[::-1]
    # get_img = lambda n: show_img(normalization(datasets[n].x[randint(0, len(datasets[n].x)-1)], 256, debug=True))
    breakpoint()

    for i in range(0, 10):
        model.fit(
            datasets=datasets,
            epochs=int(EPOCHS/10),
            batch_size=BATCH_SIZE,
            shuffle=True,
            verbose=True
        )
    
        model.save(MODEL_NAME, MODELS_PATH, overwrite=True)

