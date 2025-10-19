from simple_duck_ml import BinDatasetUnpacker, Dataset
from typing import Callable, List, Optional
from numpy.typing import NDArray
import os

class DatasetFactory:
    def load(
        self, 
        name: str,
        label: int, 
        qnt: int = 100, 
        normalization: Optional[Callable[[NDArray], NDArray]]=None
    ) -> Dataset:
        root = os.getenv("ROOT", os.getcwd())
        path = os.path.join(root, "datasets", f"{name}.bin")

        dataset = BinDatasetUnpacker(path).unpack(
            label=label,
            qnt=qnt, 
            normalization=normalization,
        )
        print(
            f"[DATASET] {name}: {len(dataset.x)} imagens carregadas "
            f"(mean={dataset.x.mean():.4f}, std={dataset.x.std():.4f})"
        )
        return dataset

    def load_all(
        self, 
        classes: List[str], 
        qnt: int = 100,
        normalization: Optional[Callable[[NDArray], NDArray]]=None,
    ) -> List[Dataset]:
        return [
            self.load(dataset, label, qnt, normalization) 
            for label, dataset in enumerate(classes)
        ]
