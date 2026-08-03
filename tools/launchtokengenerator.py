import datetime
import hashlib
import hmac
import uuid
import os

LAUNCH_TOKEN_SECRET_KEY = bytes([
    100, 95, 14, 143, 76, 117, 92, 184,
    83, 202, 241, 236, 214, 124, 240, 18
])

LAUNCH_TOKEN_SECRET_CIPHER = bytes([
    92, 57, 60, 238, 42, 69, 101, 222,
    53, 242, 146, 223, 180, 68, 149, 119,
    81, 62, 56, 234, 41, 69, 58, 129,
    49, 252, 147, 213, 224, 26, 150, 38,
    0, 111, 55, 235
])

TICKS_AT_UNIX_EPOCH = 621355968000000000

def decode_secret() -> str:
    plain = bytearray(len(LAUNCH_TOKEN_SECRET_CIPHER))
    for i, c in enumerate(LAUNCH_TOKEN_SECRET_CIPHER):
        plain[i] = c ^ LAUNCH_TOKEN_SECRET_KEY[i % len(LAUNCH_TOKEN_SECRET_KEY)]
    return plain.decode('utf-8')

def generate_launch_token() -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    seconds_since_epoch = (now - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()
    ticks = int(seconds_since_epoch * 10_000_000 + TICKS_AT_UNIX_EPOCH)

    nonce = uuid.uuid4().hex
    data = f"{ticks}|{nonce}"
    secret = decode_secret()
    mac = hmac.new(
        key=secret.encode('utf-8'),
        msg=data.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return f"{ticks}|{nonce}|{mac}"


def writelaunchtoken(tokenfile):
    token = generate_launch_token()
    os.makedirs(os.path.dirname(tokenfile), exist_ok=True)
    with open(tokenfile, "w", encoding="utf-8") as f:
        f.write(token)
    print(f"Launch token written to: {tokenfile}")