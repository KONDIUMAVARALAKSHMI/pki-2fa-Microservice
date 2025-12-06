#!/usr/bin/env python3
import os
from pathlib import Path
import time
import base64
import pyotp
from datetime import datetime, timezone

SEED_PATH = Path('/data/seed.txt')
CRON_LOG = Path('/cron/last_code.txt')


def log_line(line: str):
    CRON_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CRON_LOG, 'a') as f:
        f.write(line + '\n')


def main():
    try:
        if not SEED_PATH.exists():
            now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            log_line(f"{now} - ERROR: seed missing")
            return

        hex_seed = SEED_PATH.read_text().strip()
        seed_bytes = bytes.fromhex(hex_seed)
        b32 = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(b32, digits=6, interval=30)
        code = totp.now()

        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        log_line(f"{now} - 2FA Code: {code}")
    except Exception as e:
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        log_line(f"{now} - ERROR: {e}")


if __name__ == '__main__':
    main()
