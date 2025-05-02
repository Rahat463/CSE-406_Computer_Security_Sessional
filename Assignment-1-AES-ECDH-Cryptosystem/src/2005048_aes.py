

import os
import time
import hashlib
from BitVector import BitVector


Sbox = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
)

InvSbox = (
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D
)


AES_modulus = BitVector(bitstring='100011011')  # x^8 + x^4 + x^3 + x + 1
Mixer = [
    [BitVector(hexstring='02'), BitVector(hexstring='03'), BitVector(hexstring='01'), BitVector(hexstring='01')],
    [BitVector(hexstring='01'), BitVector(hexstring='02'), BitVector(hexstring='03'), BitVector(hexstring='01')],
    [BitVector(hexstring='01'), BitVector(hexstring='01'), BitVector(hexstring='02'), BitVector(hexstring='03')],
    [BitVector(hexstring='03'), BitVector(hexstring='01'), BitVector(hexstring='01'), BitVector(hexstring='02')]
]
InvMixer = [
    [BitVector(hexstring='0E'), BitVector(hexstring='0B'), BitVector(hexstring='0D'), BitVector(hexstring='09')],
    [BitVector(hexstring='09'), BitVector(hexstring='0E'), BitVector(hexstring='0B'), BitVector(hexstring='0D')],
    [BitVector(hexstring='0D'), BitVector(hexstring='09'), BitVector(hexstring='0E'), BitVector(hexstring='0B')],
    [BitVector(hexstring='0B'), BitVector(hexstring='0D'), BitVector(hexstring='09'), BitVector(hexstring='0E')]
]


def pad_pkcs7(bv: BitVector, block_size: int=16) -> BitVector:
    data_bytes = bv.length() // 8
    pad_len = block_size - (data_bytes % block_size)
    pad = BitVector(size=0)
    for _ in range(pad_len):
        pad += BitVector(intVal=pad_len, size=8)
    return bv + pad

def unpad_pkcs7(bv: BitVector) -> BitVector:
    pad_len = bv[-8:].intValue()
    total_bits = bv.length()
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding length")
    # extract the padding as contiguous bits
    padding_bits = bv[ total_bits - pad_len*8 : total_bits ]
    for i in range(pad_len):
        if padding_bits[i*8:(i+1)*8].intValue() != pad_len:
            raise ValueError("Invalid PKCS#7 padding")
    return bv[: total_bits - pad_len*8]

def get_round_constant(n: int) -> BitVector:
    rc = BitVector(intVal=1, size=8)
    for _ in range(n-1):
        rc = rc.gf_multiply_modular(BitVector(intVal=2, size=8), AES_modulus, 8)
    return rc

def g(word: list, round_num: int) -> list:
    rotated = word[1:] + word[:1]
    for i in range(4):
        iv = rotated[i].intValue()
        rotated[i] = BitVector(intVal=Sbox[iv], size=8)
    rotated[0] ^= get_round_constant(round_num)
    return rotated

def expand_key(matrix_key: list, round_num: int) -> list:
    cols = [[matrix_key[r][c] for r in range(4)] for c in range(4)]
    new_cols = []
    new_cols.append([cols[0][i] ^ g(cols[3], round_num)[i] for i in range(4)])
    for i in range(1, 4):
        new_cols.append([cols[i][j] ^ new_cols[i-1][j] for j in range(4)])
    return [[new_cols[c][r] for c in range(4)] for r in range(4)]

def key_expansion(key_bv: BitVector) -> list:
    key_bytes = [ key_bv[i:i+8] for i in range(0, 128, 8) ]
    matrix = [[None]*4 for _ in range(4)]
    for i in range(16):
        r, c = i%4, i//4
        matrix[r][c] = key_bytes[i]
    round_keys = [matrix]
    for rnd in range(1, 11):
        matrix = expand_key(matrix, rnd)
        round_keys.append(matrix)
    return round_keys


def sub_bytes(state):
    for r in range(4):
        for c in range(4):
            iv = state[r][c].intValue()
            state[r][c] = BitVector(intVal=Sbox[iv], size=8)

def inv_sub_bytes(state):
    for r in range(4):
        for c in range(4):
            iv = state[r][c].intValue()
            state[r][c] = BitVector(intVal=InvSbox[iv], size=8)

def shift_rows(state):
    for r in range(1, 4):
        state[r] = state[r][r:] + state[r][:r]

def inv_shift_rows(state):
    for r in range(1, 4):
        state[r] = state[r][-r:] + state[r][:-r]

def mix_columns(state):
    res = [[BitVector(intVal=0, size=8) for _ in range(4)] for _ in range(4)]
    for c in range(4):
        for r in range(4):
            for k in range(4):
                prod = Mixer[r][k].gf_multiply_modular(state[k][c], AES_modulus, 8)
                res[r][c] ^= prod
    return res

def inv_mix_columns(state):
    res = [[BitVector(intVal=0, size=8) for _ in range(4)] for _ in range(4)]
    for c in range(4):
        for r in range(4):
            for k in range(4):
                prod = InvMixer[r][k].gf_multiply_modular(state[k][c], AES_modulus, 8)
                res[r][c] ^= prod
    return res

def add_round_key(state, key_mat):
    for r in range(4):
        for c in range(4):
            state[r][c] ^= key_mat[r][c]


def encrypt_block(block_bv: BitVector, round_keys: list) -> BitVector:
    bytes_in = [block_bv[i:i+8] for i in range(0,128,8)]
    state = [[None]*4 for _ in range(4)]
    for i in range(16):
        r, c = i%4, i//4
        state[r][c] = bytes_in[i]
    add_round_key(state, round_keys[0])
    for rnd in range(1,10):
        sub_bytes(state)
        shift_rows(state)
        state = mix_columns(state)
        add_round_key(state, round_keys[rnd])
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, round_keys[10])
    out = BitVector(size=0)
    for c in range(4):
        for r in range(4):
            out += state[r][c]
    return out

def decrypt_block(block_bv: BitVector, round_keys: list) -> BitVector:
    bytes_in = [block_bv[i:i+8] for i in range(0,128,8)]
    state = [[None]*4 for _ in range(4)]
    for i in range(16):
        r, c = i%4, i//4
        state[r][c] = bytes_in[i]
    add_round_key(state, round_keys[10])
    inv_shift_rows(state)
    inv_sub_bytes(state)
    for rnd in range(9,0,-1):
        add_round_key(state, round_keys[rnd])
        state = inv_mix_columns(state)
        inv_shift_rows(state)
        inv_sub_bytes(state)
    add_round_key(state, round_keys[0])
    out = BitVector(size=0)
    for c in range(4):
        for r in range(4):
            out += state[r][c]
    return out


def encrypt_cbc(plain_bv: BitVector, round_keys: list) -> BitVector:
    padded = pad_pkcs7(plain_bv, block_size=16)
    
    print(f"In ASCII(After Padding): {padded.get_text_from_bitvector()}")
    print(f"In HEX(After Padding): {padded.get_bitvector_in_hex()}")
    
    
    iv_bytes = os.urandom(16)
    iv_bv = BitVector(intVal=int.from_bytes(iv_bytes,'big'), size=128)
    cipher = iv_bv
    prev = iv_bv
    for i in range(0, padded.length(), 128):
        blk = padded[i:i+128] ^ prev
        enc = encrypt_block(blk, round_keys)
        cipher += enc
        prev = enc
    return cipher

def decrypt_cbc(cipher_bv: BitVector, round_keys: list) -> BitVector:
    iv = cipher_bv[:128]
    ct = cipher_bv[128:]
    prev = iv
    plain = BitVector(size=0)
    for i in range(0, ct.length(), 128):
        blk = ct[i:i+128]
        dec = decrypt_block(blk, round_keys)
        plain += dec ^ prev
        prev = blk
    print("\nDeciphered Text: ");
    print("Before Unpadding:")
    print(f"In HEX: {plain.get_bitvector_in_hex()}")
    print(f"In ASCII: {plain.get_text_from_bitvector()}")
    
    return unpad_pkcs7(plain)


def main():
    key_str = input("Enter ASCII key : ")
    key_bv = BitVector(textstring=key_str)
    if key_bv.length() != 128:
        print("[!] Key length != 128 bits, deriving via SHA-256 & truncation")
        digest = hashlib.sha256(key_str.encode('utf-8')).digest()
        key_bv = BitVector(intVal=int.from_bytes(digest,'big'), size=256)[:128]
        
    t4= time.time()
    round_keys = key_expansion(key_bv)
    t5= time.time()
    
    
   
    
    pt_str = input("Enter plaintext to encrypt: ")
    pt_bv = BitVector(textstring=pt_str)
    
   
    print(f"\nKey (ASCII): {key_bv.get_text_from_bitvector()}")
    print(f"\nKey (hex): {key_bv.get_bitvector_in_hex()}")
    
    print(f"\nPlaintext (ASCII): {pt_bv.get_text_from_bitvector()}")
    print(f"\nPlaintext (hex): {pt_bv.get_bitvector_in_hex()}")
    
    
    
    t0 = time.time()
    cipher_bv = encrypt_cbc(pt_bv, round_keys)
    t1 = time.time()
    print(f"\nCiphertext (IV||CT hex): {cipher_bv.get_bitvector_in_hex()}")
    print(f"Ciphertext (IV||CT ASCII): {cipher_bv.get_text_from_bitvector()}")
    
    
    t2 = time.time()
    rec_bv = decrypt_cbc(cipher_bv, round_keys)
    t3 = time.time()
    print("After Unpadding:")
    print(f"\nIn ASCII: {rec_bv.get_text_from_bitvector()}")
    print(f"In HEX: {rec_bv.get_bitvector_in_hex()}")
    

    print("\nExecution Time Details:")
    print(f"Key Schedule time: {(t5-t4)*1000:.3f} ms")
    print(f"Encryption time: {(t1-t0)*1000:.3f} ms")
    print(f"Decryption time: {(t3-t2)*1000:.3f} ms")
    
    
if __name__ == "__main__":
    main()
