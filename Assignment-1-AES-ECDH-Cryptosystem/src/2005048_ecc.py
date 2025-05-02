

import time
import random
from typing import Union
import sympy


def generate_prime(bits: int) -> int:
    
    while True:
        # Generate a random prime with exact bit-length
        p = sympy.randprime(2**(bits-1), 2**bits - 1)
        if p % 4 == 3:
            return p


def mod_sqrt(a: int, p: int) -> Union[int, None]:
   
    
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    
    return pow(a, (p + 1) // 4, p)


def inv_mod(x: int, p: int) -> int:
    
    return pow(x, p - 2, p)

class ECPoint:
    
    __slots__ = ('x','y','a','b','p')
    def __init__(self, x, y, a, b, p):
        self.x, self.y, self.a, self.b, self.p = x, y, a, b, p
    def is_infinity(self):
        return self.x is None
    @staticmethod
    def infinity(a, b, p):
        return ECPoint(None, None, a, b, p)

def point_add(P: ECPoint, Q: ECPoint) -> ECPoint:
    
    if P.is_infinity(): return Q
    if Q.is_infinity(): return P

    p, a = P.p, P.a
    
    if P.x == Q.x and (P.y + Q.y) % p == 0:
        return ECPoint.infinity(a, P.b, p)

    
    if P.x == Q.x and P.y == Q.y:
        
        num = (3*P.x*P.x + a) % p
        den = inv_mod(2*P.y, p)
    else:
        
        num = (Q.y - P.y) % p
        den = inv_mod((Q.x - P.x) % p, p)
    lam = (num * den) % p

    xr = (lam*lam - P.x - Q.x) % p
    yr = (lam*(P.x - xr) - P.y) % p
    return ECPoint(xr, yr, a, P.b, p)

def scalar_mul(k: int, P: ECPoint) -> ECPoint:
    
    R = ECPoint.infinity(P.a, P.b, P.p)
    Q = P
    while k:
        if k & 1:
            R = point_add(R, Q)
        Q = point_add(Q, Q)
        k >>= 1
    return R


def generate_curve(k_bits: int):
    
    p = generate_prime(k_bits)
    while True:
        a = random.randrange(0, p)
        b = random.randrange(0, p)
        if (4*a*a*a + 27*b*b) % p != 0:
            break
    
    while True:
        x = random.randrange(0, p)
        rhs = (x*x*x + a*x + b) % p
        y = mod_sqrt(rhs, p)
        if y is not None:
            return p, a, b, ECPoint(x, y, a, b, p)


def time_ecdh(k_bits: int, trials: int = 5):
    
    tA = tB = tR = 0.0
    for _ in range(trials):
        p, a, b, G = generate_curve(k_bits)
        
        kA = random.randrange(1, p)
        t0 = time.perf_counter()
        A  = scalar_mul(kA, G)
        tA += time.perf_counter() - t0
        
        kB = random.randrange(1, p)
        t0 = time.perf_counter()
        B  = scalar_mul(kB, G)
        tB += time.perf_counter() - t0
        
        t0 = time.perf_counter()
        R  = scalar_mul(kA, B)
        tR += time.perf_counter() - t0
        
        assert R.x == scalar_mul(kB, A).x and R.y == scalar_mul(kB, A).y
    return tA/trials, tB/trials, tR/trials


if __name__ == '__main__':
    print(f"{'k':>5} | {'A (ms)':>10} | {'B (ms)':>10} | {'shared key R (ms)':>16}")
    print("-" * 46)
    for k in (128, 192, 256):
        a_time, b_time, r_time = time_ecdh(k)
        print(f"{k:5d} | {a_time*1000:10.6f} | {b_time*1000:10.6f} | {r_time*1000:16.6f}")
