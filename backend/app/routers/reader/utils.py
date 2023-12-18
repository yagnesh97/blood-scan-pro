import cv2
import numpy as np
import pytesseract
from cv2.typing import MatLike


def get_grayscale(image: MatLike):
    # Convert to grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def thresholding(image: MatLike):
    # Thresholding
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def image_to_text(binary_data: bytes):
    buffer = np.frombuffer(binary_data, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_ANYCOLOR)
    gray = get_grayscale(image)
    thresh = thresholding(gray)

    # Noise removal
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

    # Contrast enhancement
    contrast = cv2.equalizeHist(opening)

    # Adding custom options
    custom_config = r"--oem 3 --psm 3"
    text = pytesseract.image_to_string(contrast, config=custom_config)
    return text


def process_content(content: str) -> str:
    # Split the string into lines
    lines = content.strip().split("\n")

    # Convert the lines to a NumPy array
    lines_array = np.array(lines)

    # Keep only elements with length greater than 1
    lines_array = lines_array[np.char.str_len(lines_array) > 1]

    # Get unique elements and their indices
    unique_lines, indices = np.unique(lines_array, return_index=True)

    # Sort indices to maintain the original order
    sorted_indices = np.argsort(indices)

    # Sort unique lines based on the sorted indices
    sorted_unique_lines = unique_lines[sorted_indices]

    # Join the sorted unique lines
    processed_content = "\n".join(sorted_unique_lines)

    return processed_content
