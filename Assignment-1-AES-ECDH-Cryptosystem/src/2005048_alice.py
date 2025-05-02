import importlib.util
import socket, json, random, hashlib
from BitVector import BitVector



task1_spec = importlib.util.spec_from_file_location("aes", "./2005048_aes.py")
aes = importlib.util.module_from_spec(task1_spec)
task1_spec.loader.exec_module(aes)

task2_spec = importlib.util.spec_from_file_location("ecc", "./2005048_ecc.py")
ecc = importlib.util.module_from_spec(task2_spec)
task2_spec.loader.exec_module(ecc)


HOST = '127.0.0.1'
PORT = 65432

def derive_key_bv(R):
    
    rx = R.x.to_bytes((R.x.bit_length()+7)//8, 'big')
    digest = hashlib.sha256(rx).digest()
    return BitVector(intVal=int.from_bytes(digest, 'big'), size=256)[:128]

def main():
    
    p,a,b,G = ecc.generate_curve(128)
    kA = random.randrange(1, p)
    A  = ecc.scalar_mul(kA, G)

    
    conn = socket.socket()
    conn.connect((HOST, PORT))
    conn.send(json.dumps({
        'p':  str(p),
        'a':  str(a),
        'b':  str(b),
        'Gx': str(G.x),
        'Gy': str(G.y),
        'Ax': str(A.x),
        'Ay': str(A.y),
    }).encode())

    
    data = conn.recv(8192).decode()
    pk  = json.loads(data)
    B = ecc.ECPoint(int(pk['Bx']), int(pk['By']), a, b, p)

    
    R = ecc.scalar_mul(kA, B)
    key_bv    = derive_key_bv(R)
    round_keys = aes.key_expansion(key_bv)

    
    pt = input("Enter plaintext to send: ")
    ct_bv = aes.encrypt_cbc(BitVector(textstring=pt), round_keys)
    conn.send(json.dumps({'ct': ct_bv.get_bitvector_in_hex()}).encode())
    print("Ciphertext sent.")

    conn.close()

if __name__ == '__main__':
    main()
