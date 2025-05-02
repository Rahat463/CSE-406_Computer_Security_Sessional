import importlib.util
import socket, json, random, hashlib
from BitVector import BitVector


task1_spec = importlib.util.spec_from_file_location("aes", "./2005048_aes.py")
aes = importlib.util.module_from_spec(task1_spec)
task1_spec.loader.exec_module(aes)

task2_spec = importlib.util.spec_from_file_location("ecc", "./2005048_ecc.py")
ecc = importlib.util.module_from_spec(task2_spec)
task2_spec.loader.exec_module(ecc)


HOST = '0.0.0.0'
PORT = 65432

def derive_key_bv(R):
    rx = R.x.to_bytes((R.x.bit_length()+7)//8, 'big')
    digest = hashlib.sha256(rx).digest()
    return BitVector(intVal=int.from_bytes(digest, 'big'), size=256)[:128]

def main():
    
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(1)
    print("Bob listening on port", PORT)

    conn, addr = sock.accept()
    print("Alice connected from", addr)

    
    data = conn.recv(8192).decode()
    params = json.loads(data)
    p = int(params['p']); a = int(params['a']); b = int(params['b'])
    G = ecc.ECPoint(int(params['Gx']), int(params['Gy']), a, b, p)
    A = ecc.ECPoint(int(params['Ax']), int(params['Ay']), a, b, p)

    
    kB = random.randrange(1, p)
    B  = ecc.scalar_mul(kB, G)
    conn.send(json.dumps({'Bx': str(B.x), 'By': str(B.y)}).encode())

    
    R = ecc.scalar_mul(kB, A)
    key_bv     = derive_key_bv(R)
    round_keys = aes.key_expansion(key_bv)

    
    data = conn.recv(65536).decode()
    pkg  = json.loads(data)
    ct_bv = BitVector(hexstring=pkg['ct'])
    pt_bv = aes.decrypt_cbc(ct_bv, round_keys)
    print("Decrypted plaintext:")
    print(pt_bv.get_text_from_bitvector())

    conn.close()
    sock.close()

if __name__ == '__main__':
    main()
