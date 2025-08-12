# utils/rng_wrappers.py
from .dotnet_random import DotNetRandom

MBIG = 2147483647

def get_random_seed(a: int, b: int = 0, c: int = 0, d: int = 0, e: int = 0, *, use_legacy: bool = True) -> int:
    if use_legacy:
        return int((a % MBIG + b % MBIG + c % MBIG + d % MBIG + e % MBIG) % MBIG)
    raise NotImplementedError("use_legacy=False 留待后续实现（NetRandom / getHashFromArray）")

def get_hash_from_string(s: str) -> int:
    data = s.encode("utf-8")
    P1, P2, P3, P4, P5 = 0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F, 0x165667B1
    def rotl32(x, r): return ((x << r) & 0xFFFFFFFF) | (x >> (32 - r))
    n, i = len(data), 0
    if n >= 16:
        v1, v2, v3, v4 = (P1+P2)&0xFFFFFFFF, P2, 0, P1
        end = n - 16
        while i <= end:
            for t in range(4):
                d = int.from_bytes(data[i:i+4], "little"); i += 4
                if t == 0: v1 = (v1 + d*P2) & 0xFFFFFFFF; v1 = rotl32(v1,13); v1 = (v1*P1)&0xFFFFFFFF
                if t == 1: v2 = (v2 + d*P2) & 0xFFFFFFFF; v2 = rotl32(v2,13); v2 = (v2*P1)&0xFFFFFFFF
                if t == 2: v3 = (v3 + d*P2) & 0xFFFFFFFF; v3 = rotl32(v3,13); v3 = (v3*P1)&0xFFFFFFFF
                if t == 3: v4 = (v4 + d*P2) & 0xFFFFFFFF; v4 = rotl32(v4,13); v4 = (v4*P1)&0xFFFFFFFF
        h = (rotl32(v1,1) + rotl32(v2,7) + rotl32(v3,12) + rotl32(v4,18)) & 0xFFFFFFFF
    else:
        h = P5
    h = (h + n) & 0xFFFFFFFF
    while i + 4 <= n:
        k = int.from_bytes(data[i:i+4], "little"); i += 4
        h = (h + k*P3) & 0xFFFFFFFF; h = rotl32(h,17); h = (h*P4) & 0xFFFFFFFF
    while i < n:
        k = data[i]; i += 1
        h = (h + k*P5) & 0xFFFFFFFF; h = rotl32(h,11); h = (h*P1) & 0xFFFFFFFF
    h ^= (h >> 15); h = (h*P2) & 0xFFFFFFFF; h ^= (h >> 13); h = (h*P3) & 0xFFFFFFFF; h ^= (h >> 16)
    return h
