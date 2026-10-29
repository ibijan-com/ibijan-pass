import hmac
import hashlib
import base64
import string
import os
import struct
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# Algorithm Versioning
ALGORITHM_VERSION = "1.0"
KDF_N = 2**14
KDF_R = 8
KDF_P = 1

class CryptoError(Exception):
    pass

def _derive_key(secret: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=KDF_N,
        r=KDF_R,
        p=KDF_P
    )
    return kdf.derive(secret.encode('utf-8'))

def _canonicalize_context(service: str, account: str, revision: int, length: int, 
                          use_upper: bool, use_lower: bool, use_digits: bool, use_symbols: bool) -> bytes:
    """
    Create an unambiguous, length-prefixed byte string using struct.
    This prevents delimiter collision attacks.
    """
    svc_bytes = service.encode('utf-8')
    acct_bytes = account.encode('utf-8')
    
    # Format: ALGO_VERSION | len(svc)|svc | len(acct)|acct | revision | length | flags
    flags = (int(use_upper) << 3) | (int(use_lower) << 2) | (int(use_digits) << 1) | int(use_symbols)
    
    context = struct.pack(
        "!6sH", ALGORITHM_VERSION.encode('utf-8'), len(svc_bytes)
    ) + svc_bytes + struct.pack(
        "!H", len(acct_bytes)
    ) + acct_bytes + struct.pack(
        "!IIB", revision, length, flags
    )
    return context

def _get_deterministic_bytes(key: bytes, context: bytes, length: int) -> bytes:
    """
    Generate a deterministic byte stream using HMAC-SHA256 with a counter.
    (HMAC_DRBG style, simplified for determinism)
    """
    result = b""
    counter = 0
    while len(result) < length:
        mac = hmac.new(key, context + struct.pack("!I", counter), hashlib.sha256)
        result += mac.digest()
        counter += 1
    return result[:length]

def generate_crypto_password(
    master_secret: str,
    salt: bytes,
    service: str,
    account: str = "",
    password_revision: int = 1,
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True
) -> str:
    if not master_secret:
        raise CryptoError("Master secret cannot be empty.")
    
    if length < 4 or length > 128:
        raise CryptoError("Length must be between 4 and 128.")

    pools = []
    if use_lower: pools.append(string.ascii_lowercase)
    if use_upper: pools.append(string.ascii_uppercase)
    if use_digits: pools.append(string.digits)
    if use_symbols: pools.append("!@#$%^&*()_+-=[]{}|;:,.<>?")

    if not pools:
        raise CryptoError("At least one character type must be selected.")
        
    if length < len(pools):
        raise CryptoError(f"Length must be at least {len(pools)} to include all selected character types.")

    # 1. Derive Key and Context
    key = _derive_key(master_secret, salt)
    context = _canonicalize_context(service, account, password_revision, length, use_upper, use_lower, use_digits, use_symbols)

    # 2. Generate enough deterministic bytes (each char needs 2 bytes for rejection sampling)
    raw_bytes = _get_deterministic_bytes(key, context, length * 4 + len(pools) * 2)
    
    all_chars = "".join(pools)
    password_chars = []
    
    # 3. Ensure at least one from each pool
    byte_idx = 0
    for pool in pools:
        # Rejection sampling to avoid modulo bias
        while True:
            val = (raw_bytes[byte_idx] << 8) | raw_bytes[byte_idx + 1]
            byte_idx += 2
            if val < 65536 - (65536 % len(pool)):
                password_chars.append(pool[val % len(pool)])
                break

    # 4. Fill the rest
    remaining_length = length - len(pools)
    for i in range(remaining_length):
        while True:
            val = (raw_bytes[byte_idx] << 8) | raw_bytes[byte_idx + 1]
            byte_idx += 2
            if val < 65536 - (65536 % len(all_chars)):
                password_chars.append(all_chars[val % len(all_chars)])
                break

    # 5. Deterministic Fisher-Yates Shuffle
    for i in range(len(password_chars) - 1, 0, -1):
        while True:
            val = (raw_bytes[byte_idx] << 8) | raw_bytes[byte_idx + 1]
            byte_idx += 2
            if val < 65536 - (65536 % (i + 1)):
                j = val % (i + 1)
                password_chars[i], password_chars[j] = password_chars[j], password_chars[i]
                break

    return "".join(password_chars)

def generate_salt() -> bytes:
    return os.urandom(16)

def encode_salt(salt: bytes) -> str:
    return base64.b64encode(salt).decode('utf-8')

def decode_salt(salt_str: str) -> bytes:
    try:
        salt = base64.b64decode(salt_str.encode('utf-8'), validate=True)
        if len(salt) != 16:
            raise CryptoError("Invalid salt length.")
        return salt
    except Exception:
        raise CryptoError("Invalid Base64 salt format.")