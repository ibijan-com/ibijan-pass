import hmac
import hashlib
import base64
import string
import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

def _derive_key(secret: str, salt: bytes) -> bytes:
    """Derive a cryptographic key from the Generation Master Secret using scrypt."""
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1
    )
    return kdf.derive(secret.encode('utf-8'))

def _canonicalize_context(service: str, account: str, version: int, length: int, 
                          use_upper: bool, use_lower: bool, use_digits: bool, use_symbols: bool) -> bytes:
    """Create an unambiguous, length-prefixed byte string for HMAC input."""
    context = (
        f"v{version}|"
        f"{len(service)}:{service}|"
        f"{len(account)}:{account}|"
        f"len:{length}|"
        f"U:{1 if use_upper else 0}|"
        f"L:{1 if use_lower else 0}|"
        f"D:{1 if use_digits else 0}|"
        f"S:{1 if use_symbols else 0}"
    )
    return context.encode('utf-8')

def generate_crypto_password(
    master_secret: str,
    salt: bytes,
    service: str,
    account: str = "",
    version: int = 1,
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True
) -> str:
    """Generate a deterministic password based on the provided secret and context."""
    if not master_secret:
        raise ValueError("Master secret cannot be empty.")
    
    if length < 4 or length > 128:
        raise ValueError("Length must be between 4 and 128.")

    # 1. Derive the base key
    key = _derive_key(master_secret, salt)

    # 2. Create canonical context
    context = _canonicalize_context(service, account, version, length, use_upper, use_lower, use_digits, use_symbols)

    # 3. HMAC-SHA256
    mac = hmac.new(key, context, hashlib.sha256)
    digest = mac.digest()
    
    # 4. Password Encoding Policy
    pools = []
    if use_lower: pools.append(string.ascii_lowercase)
    if use_upper: pools.append(string.ascii_uppercase)
    if use_digits: pools.append(string.digits)
    if use_symbols: pools.append("!@#$%^&*()_+-=[]{}|;:,.<>?")

    if not pools:
        raise ValueError("At least one character type must be selected.")

    all_chars = "".join(pools)
    password_chars = []
    
    # Ensure at least one char from each pool
    required_chars = []
    for pool in pools:
        required_chars.append(pool[digest[len(required_chars)] % len(pool)])

    # Fill the rest
    remaining_length = length - len(required_chars)
    stream_bytes = digest
    counter = 0
    
    # Stretch the digest to get enough random bytes
    while len(stream_bytes) < (remaining_length * 2) + 32:
        counter += 1
        stream_bytes += hashlib.sha256(digest + counter.to_bytes(4, 'big')).digest()

    char_index = len(pools)
    for i in range(remaining_length):
        val = (stream_bytes[char_index] << 8) | stream_bytes[char_index + 1]
        password_chars.append(all_chars[val % len(all_chars)])
        char_index += 2

    # Combine and shuffle deterministically
    final_chars = required_chars + password_chars
    for i in range(len(final_chars) - 1, 0, -1):
        val = (stream_bytes[char_index] << 8) | stream_bytes[char_index + 1]
        j = val % (i + 1)
        final_chars[i], final_chars[j] = final_chars[j], final_chars[i]
        char_index += 2

    return "".join(final_chars)

def generate_salt() -> bytes:
    return os.urandom(16)

def encode_salt(salt: bytes) -> str:
    return base64.b64encode(salt).decode('utf-8')

def decode_salt(salt_str: str) -> bytes:
    return base64.b64decode(salt_str)