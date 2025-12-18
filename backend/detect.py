import cv2
import numpy as np

# ==============================
# CONFIG
# ==============================

BLOCK_SIZE = 8
EXPECTED_BITS = 256  # SHA-256 bits
MID_FREQ_Y = 4
MID_FREQ_X = 3

# Confidence thresholds (MVP-level, honest)
AUTHENTIC_THRESHOLD = 0.80
TAMPERED_THRESHOLD = 0.30


# ==============================
# WATERMARK DETECTION
# ==============================

def detect_watermark(image_path):
    """
    Detects watermark presence and estimates authenticity confidence
    """

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or invalid")

    # Convert to YCrCb and extract Y channel
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    Y_channel, _, _ = cv2.split(ycrcb)
    Y_channel = np.float32(Y_channel)

    h, w = Y_channel.shape
    extracted_bits = []
    strong_bits = 0

    # Traverse 8x8 blocks
    for row in range(0, h - BLOCK_SIZE, BLOCK_SIZE):
        for col in range(0, w - BLOCK_SIZE, BLOCK_SIZE):

            if len(extracted_bits) >= EXPECTED_BITS:
                break

            block = Y_channel[row:row + BLOCK_SIZE, col:col + BLOCK_SIZE]
            dct_block = cv2.dct(block)

            coeff = dct_block[MID_FREQ_Y, MID_FREQ_X]

            # Bit extraction
            bit = 1 if coeff > 0 else 0
            extracted_bits.append(bit)

            # Signal strength check
            if abs(coeff) > 5:   # small robustness threshold
                strong_bits += 1

        if len(extracted_bits) >= EXPECTED_BITS:
            break

    if len(extracted_bits) == 0:
        return {
            "status": "NO_VERIFIABLE_SIGNATURE",
            "confidence": 0.0
        }

    # Confidence estimation
    confidence = strong_bits / len(extracted_bits)

    # Classification
    if confidence >= AUTHENTIC_THRESHOLD:
        status = "AI_GENERATED_AUTHENTIC"
    elif confidence >= TAMPERED_THRESHOLD:
        status = "TAMPERED"
    else:
        status = "NO_VERIFIABLE_SIGNATURE"

    return {
        "status": status,
        "confidence": round(confidence, 3)
    }


# ==============================
# CLI TEST
# ==============================

if __name__ == "__main__":

    test_images = {
        "ORIGINAL": r"C:\Users\sridh\OneDrive\Desktop\AI_auth_MVP\samples\original\original.jpg",
        "AI_SIGNED": r"C:\Users\sridh\OneDrive\Desktop\AI_auth_MVP\samples\ai_generated\ai_signed.jpg"
    }

    for label, path in test_images.items():
        print(f"\nTesting {label}")
        result = detect_watermark(path)
        print(result)
