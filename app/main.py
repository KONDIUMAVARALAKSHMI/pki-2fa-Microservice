import os
import base64
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pyotp

from app.crypto_utils import load_private_key, decrypt_seed
app = FastAPI()

SEED_PATH = Path("/data/seed.txt")
PRIVATE_KEY_PATH = Path("student_private.pem")


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: str


@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(req: DecryptSeedRequest):
    if not PRIVATE_KEY_PATH.exists():
        raise HTTPException(status_code=500, detail="Private key not found")

    try:
        private_key = load_private_key(str(PRIVATE_KEY_PATH))
        hex_seed = decrypt_seed(req.encrypted_seed, private_key)
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

    os.makedirs("/data", exist_ok=True)
    SEED_PATH.write_text(hex_seed)

    return {"status": "ok"}


@app.get("/generate-2fa")
async def generate_2fa():
    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_PATH.read_text().strip()
    seed_bytes = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(b32, digits=6, interval=30)

    code = totp.now()
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
async def verify_2fa(body: Verify2FARequest):
    if not body.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_PATH.read_text().strip()
    seed_bytes = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(seed_bytes).decode("utf-8")
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    valid = totp.verify(body.code, valid_window=1)

    return {"valid": bool(valid)}


@app.get("/health")
async def health():
    return {"status": "ok"}
