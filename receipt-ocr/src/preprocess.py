from __future__ import annotations

try:
    import cv2
except ImportError:  # pragma: no cover - runtime safeguard if OpenCV is missing
    cv2 = None


def preprocess_image(image_path: str):
    if cv2 is None:
        return None

    image = cv2.imread(image_path)
    if image is None:
        return None

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
    _, thresholded = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    return thresholded
