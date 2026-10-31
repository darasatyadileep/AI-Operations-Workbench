from PIL import Image
from io import BytesIO

import cv2
import easyocr
import numpy as np


reader = easyocr.Reader(["en"], gpu=False)


def analyze_nameplate(image_bytes):

    # Decode browser upload using Pillow
    try:
        pil_image = Image.open(BytesIO(image_bytes))
        pil_image = pil_image.convert("RGB")
    except Exception as e:
        raise ValueError(
            f"Unable to open uploaded image: {e}"
        )

    # PIL image -> NumPy -> OpenCV
    img_rgb = np.array(pil_image)

    img = cv2.cvtColor(
        img_rgb,
        cv2.COLOR_RGB2BGR
    )

    # Grayscale
    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    # Improve contrast
    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # OCR
    results = reader.readtext(enhanced)

    detected_regions = []

    for bbox, text, confidence in results:

        if confidence >= 0.25:

            detected_regions.append({
                "text": text,
                "confidence": round(
                    float(confidence),
                    3
                )
            })

    raw_text = " ".join(
        item["text"]
        for item in detected_regions
    )

    text_upper = raw_text.upper()

    # -------------------------
    # Equipment identification
    # -------------------------

    equipment_type = "Not confidently detected"

    if "SCREW COMPRESSOR" in text_upper:
        equipment_type = "Screw Compressor"

    elif "AIR COMPRESSOR" in text_upper:
        equipment_type = "Air Compressor"

    elif "COMPRESSOR" in text_upper:
        equipment_type = "Compressor"

    elif "PUMP" in text_upper:
        equipment_type = "Pump"

    elif "MOTOR" in text_upper:
        equipment_type = "Motor"

    # -------------------------
    # Manufacturer
    # -------------------------

    manufacturer = "Not confidently detected"

    if "HITACHI" in text_upper:
        manufacturer = "Hitachi"

    elif "ATLAS COPCO" in text_upper:
        manufacturer = "Atlas Copco"

    elif "SIEMENS" in text_upper:
        manufacturer = "Siemens"

    return {
        "equipment_type": equipment_type,
        "manufacturer": manufacturer,
        "raw_text": raw_text,
        "detected_regions": detected_regions
    }