import cv2
import numpy as np
import hashlib
import json
import os
from datetime import datetime

# ==============================
# CONFIG
# ==============================

BLOCK_SIZE = 8
WATERMARK_STRENGTH = 10


# ==============================
# CRYPTO: CREATE SIGNATURE
# ==============================

def create_signature():
    metadata = {
        "type": "AI_GENERATED",
        "generator": "demo_ai_engine",
        "timestamp": datetime.utcnow().isoformat()
    }

    metadata_bytes = json.dumps(metadata, sort_keys=True).encode("utf-8")
    hash_bytes = hashlib.sha256(metadata_bytes).digest()
    return hash_bytes, metadata


def hash_to_bits(hash_bytes):
    bits = []
    for byte in hash_bytes:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits


# ==============================
# SIGNAL PROCESSING: DCT WATERMARK
# ==============================

def embed_watermark(image_path, output_path):
    """
    Embeds cryptographic watermark into image using DCT.
    Cloud-safe and deterministic.
    """

    # ---- Load image safely ----
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to load image")

    # Normalize color space (important for Render/OpenCV)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert to YCrCb
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = np.float32(y)

    # Create signature
    hash_bytes, _ = create_signature()
    watermark_bits = hash_to_bits(hash_bytes)

    h, w = y.shape
    bit_index = 0

    for row in range(0, h - BLOCK_SIZE, BLOCK_SIZE):
        for col in range(0, w - BLOCK_SIZE, BLOCK_SIZE):

            if bit_index >= len(watermark_bits):
                break

            block = y[row:row+BLOCK_SIZE, col:col+BLOCK_SIZE]
            dct_block = cv2.dct(block)

            coeff_y, coeff_x = 4, 3
            if watermark_bits[bit_index] == 1:
                dct_block[coeff_y, coeff_x] += WATERMARK_STRENGTH
            else:
                dct_block[coeff_y, coeff_x] -= WATERMARK_STRENGTH

            idct_block = cv2.idct(dct_block)
            y[row:row+BLOCK_SIZE, col:col+BLOCK_SIZE] = idct_block

            bit_index += 1

        if bit_index >= len(watermark_bits):
            break

    # Finalize image
    y = np.clip(y, 0, 255).astype(np.uint8)
    watermarked_ycrcb = cv2.merge([y, cr, cb])
    watermarked_rgb = cv2.cvtColor(watermarked_ycrcb, cv2.COLOR_YCrCb2RGB)
    watermarked_bgr = cv2.cvtColor(watermarked_rgb, cv2.COLOR_RGB2BGR)

    # ---- Save output (critical check) ----
    success = cv2.imwrite(output_path, watermarked_bgr)
    if not success:
        raise ValueError("Failed to write output image")

    return True
