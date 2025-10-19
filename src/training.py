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
from app.utils.img_normalization import normalization
import os


LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.001"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5"))
EPOCHS = int(os.getenv("EPOCHS", "20"))
SAMPLES_PER_CLASS = int(os.getenv("SAMPLES_PER_CLASS", "200"))

loaded_normalization = lambda img: normalization(img, (64, 64), True, True)

classes = ["ice_cream", "crab"]
datasets = DatasetFactory().load_all(classes, SAMPLES_PER_CLASS, loaded_normalization)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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

    for i in range(0, 10):
        model.fit(
            datasets=datasets,
            epochs=int(EPOCHS/10),
            batch_size=BATCH_SIZE,
            shuffle=True,
            verbose=True
        )
    
        model.save(MODEL_NAME, MODELS_PATH, overwrite=True)
