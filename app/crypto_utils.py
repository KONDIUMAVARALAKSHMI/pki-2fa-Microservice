import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key(key_path: str):
    with open(key_path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

def decrypt_seed(encrypted_seed_b64: str, private_key):
    encrypted_seed = base64.b64decode(encrypted_seed_b64)

    decrypted_bytes = private_key.decrypt(
        encrypted_seed,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    hex_seed = decrypted_bytes.decode("utf-8")

    # Validate: must be 64 hex characters
    if len(hex_seed) != 64 or not all(c in "0123456789abcdef" for c in hex_seed.lower()):
        raise ValueError("Invalid hex seed format")

    return hex_seed
