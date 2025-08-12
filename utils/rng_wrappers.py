# utils/rng_wrappers.py
# 1.6 的 RNG 封装（legacy 路径），严格对齐 mouseypounds 的 JS 语义

import math
from .dotnet_random import DotNetRandom

MBIG = 2147483647  # 2^31 - 1

def js_mod(a, m):
    """JS 风格取模：向零截断的余数（可能为负）"""
    q = int(a / m)  # 向零截断，模拟 JS 的除法取整
    return a - q * m

def get_random_seed(a, b = 0, c = 0, d = 0, e = 0, *, use_legacy: bool = True) -> int:
    """
    legacy: Math.floor((a % M + b % M + c % M + d % M + e % M) % M)
    注意：JS 用 Math.floor（向下取整），不能用 Python 的 int()（向零截断）。
    返回值标准化为 int32（可能为负）。
    """
    if use_legacy:
        total = js_mod(a, MBIG) + js_mod(b, MBIG) + js_mod(c, MBIG) + js_mod(d, MBIG) + js_mod(e, MBIG)
        total = js_mod(total, MBIG)
        total = math.floor(total)  # 关键修复：与 JS Math.floor 对齐

        # 规范到 int32 带符号范围
        total &= 0xFFFFFFFF
        if total >= 2**31:
            total -= 2**32
        return total
    else:
        raise NotImplementedError("use_legacy=False 留待后续实现（NetRandom / getHashFromArray）")

def get_hash_from_string(s: str) -> int:
    """
    xxHash32 (h32, seed=0) over UTF-8 bytes.
    Returns signed 32-bit int (may be negative), matching JS XXH.h32().toNumber().
    """
    data = s.encode("utf-8")

    PRIME32_1 = 0x9E3779B1
    PRIME32_2 = 0x85EBCA77
    PRIME32_3 = 0xC2B2AE3D
    PRIME32_4 = 0x27D4EB2F
    PRIME32_5 = 0x165667B1

    def rotl32(x, r):
        return ((x << r) & 0xFFFFFFFF) | (x >> (32 - r))

    length = len(data)
    idx = 0
    seed = 0

    if length >= 16:
        v1 = (seed + PRIME32_1 + PRIME32_2) & 0xFFFFFFFF
        v2 = (seed + PRIME32_2) & 0xFFFFFFFF
        v3 = (seed + 0) & 0xFFFFFFFF
        v4 = (seed - PRIME32_1) & 0xFFFFFFFF

        limit = length - 16
        while idx <= limit:
            d1 = int.from_bytes(data[idx:idx+4], "little"); idx += 4
            v1 = (v1 + d1 * PRIME32_2) & 0xFFFFFFFF
            v1 = rotl32(v1, 13)
            v1 = (v1 * PRIME32_1) & 0xFFFFFFFF

            d2 = int.from_bytes(data[idx:idx+4], "little"); idx += 4
            v2 = (v2 + d2 * PRIME32_2) & 0xFFFFFFFF
            v2 = rotl32(v2, 13)
            v2 = (v2 * PRIME32_1) & 0xFFFFFFFF

            d3 = int.from_bytes(data[idx:idx+4], "little"); idx += 4
            v3 = (v3 + d3 * PRIME32_2) & 0xFFFFFFFF
            v3 = rotl32(v3, 13)
            v3 = (v3 * PRIME32_1) & 0xFFFFFFFF

            d4 = int.from_bytes(data[idx:idx+4], "little"); idx += 4
            v4 = (v4 + d4 * PRIME32_2) & 0xFFFFFFFF
            v4 = rotl32(v4, 13)
            v4 = (v4 * PRIME32_1) & 0xFFFFFFFF

        h32 = (rotl32(v1, 1) + rotl32(v2, 7) + rotl32(v3, 12) + rotl32(v4, 18)) & 0xFFFFFFFF
    else:
        h32 = (seed + PRIME32_5) & 0xFFFFFFFF

    h32 = (h32 + length) & 0xFFFFFFFF

    # process remaining 4-byte chunks
    while idx + 4 <= length:
        k1 = int.from_bytes(data[idx:idx+4], "little"); idx += 4
        h32 = (h32 + k1 * PRIME32_3) & 0xFFFFFFFF
        h32 = rotl32(h32, 17)
        h32 = (h32 * PRIME32_4) & 0xFFFFFFFF

    # process remaining tail bytes
    while idx < length:
        k1 = data[idx]; idx += 1
        h32 = (h32 + k1 * PRIME32_5) & 0xFFFFFFFF
        h32 = rotl32(h32, 11)
        h32 = (h32 * PRIME32_1) & 0xFFFFFFFF

    # avalanche
    h32 ^= (h32 >> 15)
    h32 = (h32 * PRIME32_2) & 0xFFFFFFFF
    h32 ^= (h32 >> 13)
    h32 = (h32 * PRIME32_3) & 0xFFFFFFFF
    h32 ^= (h32 >> 16)

    # convert to signed 32-bit
    if h32 >= 2**31:
        h32 -= 2**32
    return h32
