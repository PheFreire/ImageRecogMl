from numpy.typing import NDArray
from typing import Optional, Tuple
import numpy as np
import cv2

def normalization(
    img: NDArray,
    resize: Optional[Tuple[int, int]]=None,
    binarize: bool=False, 
    black_background: bool=False,
) -> NDArray:
    # Resize | normalize | invert to black background
    if resize is not None:
        img = cv2.resize(img, resize).astype(np.float64)

    if binarize:
        img = img / 255.0

    if black_background:
        img = 1.0 - img

    return img
