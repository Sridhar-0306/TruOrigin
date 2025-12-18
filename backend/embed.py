import cv2
import numpy as np
import hashlib
import json
from datetime import datetime

# ==============================
# CONFIG
# ==============================

BLOCK_SIZE = 8
WATERMARK_STRENGTH = 10  # small value = invisible, robust enough


# ==============================
# CRYPTO: CREATE SIGNATURE
# ==============================

def create_signature():
    """
    Simulates AI generation metadata and creates SHA-256 hash
    """
    metadata = {
        "type": "AI_GENERATED",
        "generator": "demo_ai_engine",
        "timestamp": datetime.utcnow().isoformat()
    }

    metadata_bytes = json.dumps(metadata, sort_keys=True).encode("utf-8")
    hash_bytes = hashlib.sha256(metadata_bytes).digest()

    return hash_bytes, metadata


def hash_to_bits(hash_bytes):
    """
    Converts hash bytes to bit array (0/1)
    """
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
    Embeds cryptographic watermark into image using DCT (Y channel)
    """

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or invalid")

    # Convert to YCrCb (preserve color)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    Y_channel, Cr, Cb = cv2.split(ycrcb)

    Y_channel = np.float32(Y_channel)

    # Create signature
    hash_bytes, metadata = create_signature()
    watermark_bits = hash_to_bits(hash_bytes)

    h, w = Y_channel.shape
    bit_index = 0

    # Process 8x8 blocks
    for row in range(0, h - BLOCK_SIZE, BLOCK_SIZE):
        for col in range(0, w - BLOCK_SIZE, BLOCK_SIZE):

            if bit_index >= len(watermark_bits):
                break

            block = Y_channel[row:row + BLOCK_SIZE, col:col + BLOCK_SIZE]
            dct_block = cv2.dct(block)

            # Mid-frequency coefficient
            coeff_y, coeff_x = 4, 3

            if watermark_bits[bit_index] == 1:
                dct_block[coeff_y, coeff_x] += WATERMARK_STRENGTH
            else:
                dct_block[coeff_y, coeff_x] -= WATERMARK_STRENGTH

            # Inverse DCT
            idct_block = cv2.idct(dct_block)
            Y_channel[row:row + BLOCK_SIZE, col:col + BLOCK_SIZE] = idct_block

            bit_index += 1

        if bit_index >= len(watermark_bits):
            break

    # Reconstruct color image
    Y_channel = np.clip(Y_channel, 0, 255).astype(np.uint8)
    watermarked_ycrcb = cv2.merge([Y_channel, Cr, Cb])
    watermarked_image = cv2.cvtColor(watermarked_ycrcb, cv2.COLOR_YCrCb2BGR)

    # Save image
    cv2.imwrite(output_path, watermarked_image)

    return {
        "status": "AI_IMAGE_SIGNED",
        "output": output_path,
        "metadata": metadata
    }


# ==============================
# CLI TEST
# ==============================

if __name__ == "__main__":
    input_image = r"C:\Users\sridh\OneDrive\Desktop\AI_auth_MVP\samples\original\original.jpg"
    output_image = r"C:\Users\sridh\OneDrive\Desktop\AI_auth_MVP\samples\ai_generated\ai_signed.jpg"

    result = embed_watermark(input_image, output_image)
    print("Embedding completed:")
    print(result)


