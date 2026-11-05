from PIL import Image
from io import BytesIO

import cv2
import easyocr
import numpy as np
import re


reader = None


def get_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(["en"], gpu=False)
    return reader


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
    results = get_reader().readtext(enhanced)

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

    # -------------------------
    # Lightweight structured extraction
    # -------------------------
    def match_value(patterns):
        for pattern in patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                return match.group(1).strip(" :-")
        return None

    structured_fields = {
        "model": match_value([
            r"(?:MODEL|TYPE)\s*(?:NO\.?|NUMBER|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-\./]{2,24})"
        ]),
        "serial_number": match_value([
            r"(?:SERIAL|S\s*/?\s*N|SER\.?\s*NO\.?)\s*[:\-#]?\s*([A-Z0-9][A-Z0-9\-\./]{2,28})"
        ]),
        "rated_power": match_value([
            r"([0-9]+(?:\.[0-9]+)?\s*(?:KW|MW|HP))"
        ]),
        "voltage": match_value([
            r"([0-9]+(?:\.[0-9]+)?\s*(?:KV|V))\b"
        ]),
        "frequency": match_value([
            r"([0-9]+(?:\.[0-9]+)?\s*HZ)\b"
        ]),
        "pressure_rating": match_value([
            r"([0-9]+(?:\.[0-9]+)?\s*(?:BAR|BARG|PSI|KPA|MPA))\b"
        ])
    }

    confidences = [item["confidence"] for item in detected_regions]
    average_confidence = (
        round(float(np.mean(confidences)), 3)
        if confidences
        else 0.0
    )

    return {
        "equipment_type": equipment_type,
        "manufacturer": manufacturer,
        "average_ocr_confidence": average_confidence,
        "structured_fields": structured_fields,
        "raw_text": raw_text,
        "detected_regions": detected_regions
    }
