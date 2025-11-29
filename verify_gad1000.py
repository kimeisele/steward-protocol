import requests
import time
import json
import base64
import hashlib
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sigencode_string

API_URL = "http://127.0.0.1:8000"
API_KEY = "steward-secret-key"


def test_health():
    print("Testing Health...")
    try:
        r = requests.get(f"{API_URL}/health")
        print(f"Health: {r.status_code} {r.json()}")
        assert r.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        exit(1)


def test_frontend():
    print("Testing Frontend Mount...")
    try:
        r = requests.get(f"{API_URL}/")
        print(f"Frontend: {r.status_code}")
        assert r.status_code == 200
        assert "<title>Agentic World | Public Access</title>" in r.text
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        exit(1)


def generate_identity():
    print("Generating Identity...")
    sk = SigningKey.generate(curve=NIST256p, hashfunc=hashlib.sha256)
    vk = sk.get_verifying_key()
    # Export public key as SPKI (SubjectPublicKeyInfo) DER, then base64?
    # Frontend uses: exportKey("spki") -> ArrayBuffer -> Hex
    # Wait, frontend sends HEX string of SPKI.
    # Python ecdsa `to_der()` gives SPKI? No, `to_der()` gives X.509 SubjectPublicKeyInfo if using `VerifyingKey`.
    # Let's check `steward/crypto.py` expectation.
    # `steward/crypto.py` expects base64 of the key content (without PEM headers).
    # But `gateway/api.py` receives `public_key` from frontend.
    # Frontend sends HEX.
    # `gateway/api.py` passes it to `verify_signature`.
    # `verify_signature` expects base64.
    # Uh oh. Frontend sends HEX, backend expects Base64?
    # Let's check `identity_wallet.js`: `_arrayBufferToHex(publicKey)`.
    # Let's check `gateway/api.py`: `verify_signature(payload, signature, public_key)`.
    # Let's check `steward/crypto.py`: `_load_public_key` takes base64.
    # AND `_load_public_key` wraps it in `-----BEGIN PUBLIC KEY-----`.
    # `VerifyingKey.from_pem` handles base64 inside PEM.
    # If I pass HEX to `verify_signature`, `_load_public_key` will fail to parse it as PEM if it's not base64.
    # HEX is NOT Base64.
    # I need to convert HEX to Base64 in `gateway/api.py` OR change frontend to send Base64.
    # The user instructions for `identity_wallet.js` explicitly implemented `_arrayBufferToHex`.
    # So the frontend sends HEX.
    # The backend MUST handle HEX or convert it.
    # `steward/crypto.py` expects Base64.
    # I should update `gateway/api.py` to convert Hex to Base64 before calling `verify_signature`.
    # OR update `identity_wallet.js` to send Base64.
    # Updating `identity_wallet.js` is cleaner for standard web crypto usage (usually Base64).
    # But the user provided the `_arrayBufferToHex` helper in the prompt.
    # I should probably stick to the user's prompt for JS but fix the backend to handle it.
    # Wait, `verify_signature` in `steward/crypto.py` takes `public_key_b64`.
    # If I pass hex, it will fail.
    # I will update `gateway/api.py` to convert hex to base64.

    # But first, let's finish the script assuming I fix it.
    return sk, vk


def test_registration(sk, vk):
    print("Testing Registration...")
    # Simulate frontend: SPKI DER -> Hex
    spki_der = vk.to_der()  # This is SPKI
    public_key_hex = spki_der.hex()

    payload = {
        "agent_id": "HIL",
        "public_key": public_key_hex,
        "timestamp": int(time.time() * 1000),
    }

    r = requests.post(f"{API_URL}/v1/register_human", json=payload)
    print(f"Registration: {r.status_code} {r.json()}")
    assert r.status_code == 200
    return public_key_hex


def test_signed_chat(sk, vk, public_key_hex):
    print("Testing Signed Chat...")
    message = "Hello Agent City"
    timestamp = int(time.time() * 1000)

    # Payload to sign: JSON string {"message":..., "timestamp":...}
    # Frontend uses JSON.stringify which produces compact JSON.
    payload_dict = {"message": message, "timestamp": timestamp}
    payload_str = json.dumps(payload_dict, separators=(",", ":"))

    # Sign
    sig = sk.sign(payload_str.encode("utf-8"), hashfunc=hashlib.sha256, sigencode=sigencode_string)
    # Frontend sends signature as HEX?
    # `identity_wallet.js`: `signature: this._arrayBufferToHex(signature)`
    # So signature is HEX.
    # `gateway/api.py` calls `verify_signature(payload, signature, public_key)`.
    # `steward/crypto.py` `verify_signature` expects `signature_b64`.
    # So backend expects Base64 for signature too!
    # I need to convert signature from Hex to Base64 in backend too.

    sig_hex = sig.hex()

    chat_payload = {
        "agent_id": "HIL",
        "message": message,
        "timestamp": timestamp,
        "signature": sig_hex,
        "context": {},
    }

    headers = {"x-api-key": API_KEY}
    r = requests.post(f"{API_URL}/v1/chat", json=chat_payload, headers=headers)
    print(f"Chat Status: {r.status_code}")
    print(f"Chat Response: {r.text}")
    assert r.status_code == 200
    assert r.json()["status"] == "success"


if __name__ == "__main__":
    test_health()
    test_frontend()
    sk, vk = generate_identity()
    pk_hex = test_registration(sk, vk)
    test_signed_chat(sk, vk, pk_hex)
    print("✅ ALL TESTS PASSED")
