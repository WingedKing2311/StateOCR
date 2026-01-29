import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def run_ocr(image):
    """
    image: preprocessed NumPy image (from OpenCV)
    returns: combined OCR text
    """
    results = reader.readtext(image)

    lines = []
    for (_, text, conf) in results:
        if conf > 0.4:  # filter garbage
            lines.append(text)

    return "\n".join(lines)
