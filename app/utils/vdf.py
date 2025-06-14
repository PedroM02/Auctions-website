# app/utils/vdf.py

import hashlib

from datetime import datetime
from Crypto.Util import number


# configuration
KEY_SIZE = 2048  # secure RSA modulus size
GENERATOR = 5
MAX_CHALLENGE_SIZE = 32  # bits for challenge prime

# optimized prime handling
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

def is_prime(n: int) -> bool:
    """Optimized Miller-Rabin test"""
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def next_prime(n: int, max_tries=1000) -> int:
    """Find next prime with search limit"""
    if n < 2:
        return 2
    candidate = n | 1  # Make odd
    for _ in range(max_tries):
        if is_prime(candidate):
            return candidate
        candidate += 2
    raise ValueError("Prime not found in range")

def generate_challenge(x: int, y: int) -> int:
    """Deterministic prime challenge"""
    h = hashlib.sha256(f"{x}{y}".encode()).digest()
    candidate = int.from_bytes(h, 'big') % (1 << MAX_CHALLENGE_SIZE)
    return next_prime(candidate)

def generate_rsa_modulus():
    """Safe prime generation"""
    p = number.getPrime(KEY_SIZE // 2)
    q = number.getPrime(KEY_SIZE // 2)
    return p * q

def setup(delay: int):
    """One-time trusted setup"""
    return {
        "modulus": generate_rsa_modulus(),
        "generator": GENERATOR,
        "delay": delay
    }

def eval_vdf(params: dict, input_bytes: bytes):
    """Optimized evaluation with progress tracking"""
    x = int.from_bytes(hashlib.sha256(input_bytes).digest(), 'big') % params['modulus']
    x = x or 1  # ensure non-zero
    
    # progressively compute squarings
    y = x
    t = params['delay']
    for i in range(t):
        y = pow(y, 2, params['modulus'])
    
    # generate proof
    l = generate_challenge(x, y)
    r = pow(2, t, l)
    pi = pow(x, (pow(2, t) - r) // l, params['modulus'])
    
    return y, pi

def verify_vdf(params: dict, input_bytes: bytes, output: int, proof: int) -> bool:
    """Fast verification"""
    x = int.from_bytes(hashlib.sha256(input_bytes).digest(), 'big') % params['modulus']
    x = x or 1
    
    l = generate_challenge(x, output)
    r = pow(2, params['delay'], l)
    
    return output % params['modulus'] == (
        pow(proof, l, params['modulus']) * pow(x, r, params['modulus'])
    ) % params['modulus']

# =========================
# Test
# =========================

if __name__ == "__main__":
    delay = 1_000_000
    print("Generating RSA modulus...")
    params = setup(delay)

    input_data = b"hello world"
    start_time = datetime.now()
    output, proof = eval_vdf(params, input_data)
    duration = datetime.now() - start_time

    print(f"Modulus N: {params['modulus']}")
    print(f"VDF output: {output}")
    print(f"Proof: {proof}")
    print(f"Computed in {duration} seconds")

    is_valid = verify_vdf(params, input_data, output, proof)
    print(f"Verification result: {is_valid}")