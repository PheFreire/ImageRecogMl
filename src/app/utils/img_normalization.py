import cv2
import numpy as np
from numpy.typing import NDArray
from random import uniform, randint, random
import uuid


def debug_log(prefix: str, msg: str, debug: bool):
    if debug:
        print(f"[DEBUG {prefix}] {msg}")


def center_image(img: NDArray[np.uint8], size: int = 256) -> NDArray[np.uint8]:
    # img binária: 0 = preto, 255 = branco
    coords = cv2.findNonZero(255 - img)
    if coords is None:
        return np.ones((size, size), dtype=np.uint8) * 255

    x, y, w, h = cv2.boundingRect(coords)
    cropped = img[y:y+h, x:x+w]

    # novo fundo branco
    centered = np.ones((size, size), dtype=np.uint8) * 255

    # redimensionar para caber
    factor = min(size / w, size / h) * 0.8
    resized = cv2.resize(cropped, (int(w * factor), int(h * factor)))

    # centralizar
    x_offset = (size - resized.shape[1]) // 2
    y_offset = (size - resized.shape[0]) // 2
    centered[y_offset:y_offset + resized.shape[0], x_offset:x_offset + resized.shape[1]] = resized
    return centered


def augment_sketch(
    img: NDArray[np.uint8],
    canvas_size: int = 256,
    min_scale: float = 0.8,
    max_scale: float = 1.4,
    max_rotation: int = 25,
    thickness_range=(1, 5),
    debug: bool = True,
) -> NDArray[np.uint8]:

    # Debug prefix for multi-image tracking
    prefix = uuid.uuid4().hex[:6]
    debug_log(prefix, "--- START AUGMENT ---", debug)

    coords = cv2.findNonZero(255 - img)
    if coords is None:
        debug_log(prefix, "NO STROKES FOUND -> RETURN IMG", debug)
        return img

    x, y, w, h = cv2.boundingRect(coords)
    debug_log(prefix, f"CROP -> w:{w}, h:{h}", debug)
    cropped = img[y:y+h, x:x+w]

    # Escala aleatoria
    factor = uniform(min_scale, max_scale)
    new_w = max(1, int(w * factor))
    new_h = max(1, int(h * factor))
    debug_log(prefix, f"SCALE -> factor:{factor:.2f}, new:{new_w}x{new_h}", debug)

    # Rejeitar imagens muito pequenas (perdem forma)
    if new_w < 20 or new_h < 20:
        debug_log(prefix, "FALLBACK: too small after scale", debug)
        return center_image(img)

    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_NEAREST)

    # Rotação aleatoria
    angle = uniform(-max_rotation, max_rotation)
    rotation = cv2.getRotationMatrix2D((new_w / 2, new_h / 2), angle, 1.0)
    rotated = cv2.warpAffine(resized, rotation, (new_w, new_h), borderValue=255)
    debug_log(prefix, f"ROTATE -> angle:{angle:.1f}", debug)

    # Segurança contra overflow de tamanho apos rotação
    if new_w > canvas_size or new_h > canvas_size:
        scale = min(canvas_size / new_w, canvas_size / new_h)
        new_w = max(1, int(new_w * scale))
        new_h = max(1, int(new_h * scale))
        rotated = cv2.resize(rotated, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        debug_log(prefix, f"SCALE FIX -> {new_w}x{new_h}", debug)

    # Regras para decidir tamanho da grossura
    min_dim = min(new_w, new_h)
    if min_dim <= 80:
        thickness = 1  # nunca dilatar -> figura muito fina
        debug_log(prefix, "SKIP DILATE -> too thin", debug)
    
    else:
        thickness = randint(*thickness_range)

        # segurança extra: limite baseado no tamanho real
        if min_dim <= 120:
            thickness = min(thickness, 2)

        if thickness > 1:
            rotated = cv2.dilate(rotated, np.ones((thickness, thickness), np.uint8))
            debug_log(prefix, f"DILATE -> thickness:{thickness}", debug)


    # novo fundo branco
    canvas = np.ones((canvas_size, canvas_size), dtype=np.uint8) * 255

    # Margens mínimas obrigatórias
    margin = 14
    max_x = max(0, canvas_size - new_w - margin)
    max_y = max(0, canvas_size - new_h - margin)

    if max_x <= margin or max_y <= margin:
        debug_log(prefix, "FALLBACK: near edges -> center instead", debug)
        return center_image(img)

    # posição aleatoria com margem
    x_offset = randint(margin, max_x)
    y_offset = randint(margin, max_y)

    # proibir tocar as 4 bordas
    if (
        x_offset <= margin or
        y_offset <= margin or
        x_offset + new_w >= canvas_size - margin or
        y_offset + new_h >= canvas_size - margin
    ):
        debug_log(prefix, "FALLBACK: hit border triggers center", debug)
        return center_image(img)

    # composição segura
    canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = rotated
    debug_log(prefix, f"PLACE -> pos:({x_offset},{y_offset}), size:{new_w}x{new_h}", debug)
    debug_log(prefix, "--- END AUGMENT ---", debug)
    return canvas


def normalization(
    img: NDArray,
    resize: int = 256,
    apply_augment: bool = True,
    augment_prob: float = 0.5,
    black_background: bool = True,
    debug: bool = False,
) -> NDArray[np.float64]:

    # Padroniza primeiro
    img = center_image(img)

    # Aplica augmentation apenas às vezes
    if apply_augment and random() < augment_prob:
        img = augment_sketch(img, debug=debug)

    # Redimensionamento
    img = cv2.resize(img, (resize, resize)).astype(np.float64)

    # Normaliza para [0,1] e inverte para fundo preto
    img /= 127.5
    img = 1.0 - img if black_background else img

    return img
