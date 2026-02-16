import base64
import json
import time
import io
import stepic
from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes = b'static_salt_stego_bot') -> bytes:
    """Derive encryption key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(text: str, password: str, ttl_minutes: int) -> bytes:
    """Encrypt text with password and TTL"""
    key = derive_key(password)
    f = Fernet(key)
    
    payload = {
        "text": text,
        "expiry": time.time() + (ttl_minutes * 60)
    }
    json_bytes = json.dumps(payload).encode('utf-8')
    return f.encrypt(json_bytes)

def decrypt_data(encrypted_data: bytes, password: str) -> str:
    """Decrypt data and validate TTL"""
    try:
        key = derive_key(password)
        f = Fernet(key)
        decrypted_bytes = f.decrypt(encrypted_data)
        payload = json.loads(decrypted_bytes.decode('utf-8'))
        
        if time.time() > payload["expiry"]:
            return "⛔ Message lifetime expired"
        
        return f"🔓 Secret message:\n\n{payload['text']}"
    except Exception:
        return "❌ Invalid password or corrupted data"

def embed_data(image_bytes: bytes, data: bytes) -> bytes:
    """Embed encrypted data in image using LSB steganography"""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    stego_img = stepic.encode(img, data)
    
    output = io.BytesIO()
    stego_img.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()

def extract_data(image_bytes: bytes) -> bytes:
    """Extract hidden data from image"""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    decoded_str = stepic.decode(img)
    return decoded_str.encode('latin1')