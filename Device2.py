# DES Device 2 - Real Network Implementation
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import threading
import socket

# DES ALGORITHM
IP = [58, 50, 42, 34, 26, 18, 10, 2,
      60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6,
      64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17, 9, 1,
      59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5,
      63, 55, 47, 39, 31, 23, 15, 7]

IP_INV = [40, 8, 48, 16, 56, 24, 64, 32,
          39, 7, 47, 15, 55, 23, 63, 31,
          38, 6, 46, 14, 54, 22, 62, 30,
          37, 5, 45, 13, 53, 21, 61, 29,
          36, 4, 44, 12, 52, 20, 60, 28,
          35, 3, 43, 11, 51, 19, 59, 27,
          34, 2, 42, 10, 50, 18, 58, 26,
          33, 1, 41, 9, 49, 17, 57, 25]

E = [32, 1, 2, 3, 4, 5,
     4, 5, 6, 7, 8, 9,
     8, 9, 10, 11, 12, 13,
     12, 13, 14, 15, 16, 17,
     16, 17, 18, 19, 20, 21,
     20, 21, 22, 23, 24, 25,
     24, 25, 26, 27, 28, 29,
     28, 29, 30, 31, 32, 1]

P = [16, 7, 20, 21, 29, 12, 28, 17,
     1, 15, 23, 26, 5, 18, 31, 10,
     2, 8, 24, 14, 32, 27, 3, 9,
     19, 13, 30, 6, 22, 11, 4, 25]

S_BOX = [
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]

PC1 = [57, 49, 41, 33, 25, 17, 9,
       1, 58, 50, 42, 34, 26, 18,
       10, 2, 59, 51, 43, 35, 27,
       19, 11, 3, 60, 52, 44, 36,
       63, 55, 47, 39, 31, 23, 15,
       7, 62, 54, 46, 38, 30, 22,
       14, 6, 61, 53, 45, 37, 29,
       21, 13, 5, 28, 20, 12, 4]

PC2 = [14, 17, 11, 24, 1, 5,
       3, 28, 15, 6, 21, 10,
       23, 19, 12, 4, 26, 8,
       16, 7, 27, 20, 13, 2,
       41, 52, 31, 37, 47, 55,
       30, 40, 51, 45, 33, 48,
       44, 49, 39, 56, 34, 53,
       46, 42, 50, 36, 29, 32]

SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

def permute(block, table):
    return ''.join([block[i - 1] for i in table])

def left_shift(bits, n):
    return bits[n:] + bits[:n]

def xor(bits1, bits2):
    return ''.join(['0' if bits1[i] == bits2[i] else '1' for i in range(len(bits1))])

def s_box_substitution(bits):
    result = ''
    for i in range(8):
        chunk = bits[i * 6:(i + 1) * 6]
        row = int(chunk[0] + chunk[5], 2)
        col = int(chunk[1:5], 2)
        val = S_BOX[i][row][col]
        result += format(val, '04b')
    return result

def generate_keys(key):
    key = permute(key, PC1)
    C = key[:28]
    D = key[28:]
    keys = []
    for i in range(16):
        C = left_shift(C, SHIFT_SCHEDULE[i])
        D = left_shift(D, SHIFT_SCHEDULE[i])
        combined = C + D
        round_key = permute(combined, PC2)
        keys.append(round_key)
    return keys

def des_round(right, round_key):
    expanded = permute(right, E)
    xored = xor(expanded, round_key)
    substituted = s_box_substitution(xored)
    result = permute(substituted, P)
    return result

def des_encrypt_block(block, keys):
    block = permute(block, IP)
    left = block[:32]
    right = block[32:]
    for i in range(16):
        temp = right
        right = xor(left, des_round(right, keys[i]))
        left = temp
    combined = right + left
    ciphertext = permute(combined, IP_INV)
    return ciphertext

def des_decrypt_block(block, keys):
    return des_encrypt_block(block, keys[::-1])

def string_to_bits(text):
    return ''.join([format(ord(c), '08b') for c in text])

def bits_to_string(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def pad_text(text):
    padding_length = 8 - (len(text) % 8)
    if padding_length == 8:
        padding_length = 0
    return text + chr(padding_length) * padding_length

def unpad_text(text):
    if not text:
        return text
    padding_length = ord(text[-1])
    if padding_length < 8:
        return text[:-padding_length] if padding_length > 0 else text
    return text

def des_encrypt(plaintext, key):
    plaintext = pad_text(plaintext)
    if len(key) < 8:
        key = key.ljust(8, '0')
    elif len(key) > 8:
        key = key[:8]
    key_bits = string_to_bits(key)
    keys = generate_keys(key_bits)
    plaintext_bits = string_to_bits(plaintext)
    ciphertext_bits = ''
    for i in range(0, len(plaintext_bits), 64):
        block = plaintext_bits[i:i+64]
        if len(block) == 64:
            ciphertext_bits += des_encrypt_block(block, keys)
    ciphertext_hex = hex(int(ciphertext_bits, 2))[2:].upper()
    return ciphertext_hex

def des_decrypt(ciphertext_hex, key):
    if len(key) < 8:
        key = key.ljust(8, '0')
    elif len(key) > 8:
        key = key[:8]
    key_bits = string_to_bits(key)
    keys = generate_keys(key_bits)
    ciphertext_bits = bin(int(ciphertext_hex, 16))[2:].zfill(len(ciphertext_hex) * 4)
    plaintext_bits = ''
    for i in range(0, len(ciphertext_bits), 64):
        block = ciphertext_bits[i:i+64]
        if len(block) == 64:
            plaintext_bits += des_decrypt_block(block, keys)
    plaintext = bits_to_string(plaintext_bits)
    plaintext = unpad_text(plaintext)
    return plaintext

# NETWORK CONFIGURATION
def get_local_ip():
    """Mendapatkan IP address lokal laptop ini"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

# Global variable untuk menyimpan IP Device 1
DEVICE1_IP = None

# HTTP SERVER
class DESRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        print("\n" + "="*50)
        print("PESAN DITERIMA DARI DEVICE 1")
        print("="*50)
        print(f"Ciphertext: {data['ciphertext']}")
        print(f"Key       : {data['key']}")
        
        try:
            plaintext = des_decrypt(data['ciphertext'], data['key'])
            print(f"Plaintext : {plaintext}")
        except Exception as e:
            print(f"Error dekripsi: {e}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'received'}).encode())
    
    def log_message(self, format, *args):
        pass

def start_server(host):
    server = HTTPServer((host, 8080), DESRequestHandler)
    print(f"Server berjalan di {host}:8080")
    print("Menunggu pesan dari Device 1...")
    server.serve_forever()

def send_to_device1(ciphertext, key):
    global DEVICE1_IP
    url = f'http://{DEVICE1_IP}:8080'
    headers = {'Content-Type': 'application/json'}
    data = {
        'ciphertext': ciphertext,
        'key': key
    }
    
    try:
        req = urllib.request.Request(url, json.dumps(data).encode('utf-8'), headers)
        response = urllib.request.urlopen(req, timeout=5)
        print("✓ Ciphertext berhasil dikirim ke Device 1")
    except Exception as e:
        print(f"✗ Gagal mengirim ke Device 1: {e}")
        print(f"  Pastikan Device 1 sudah berjalan di {DEVICE1_IP}")

def main():
    global DEVICE1_IP
    
    print("=" * 50)
    print("DEVICE 2 - DES ENCRYPTION")
    print("=" * 50)
    
    # Dapatkan IP lokal
    local_ip = get_local_ip()
    print(f"\nIP Address Device 2 (Laptop ini): {local_ip}")
    
    # Input IP Device 1
    DEVICE1_IP = input("Masukkan IP Address Device 1 (Laptop lain): ").strip()
    
    print(f"\nKonfigurasi:")
    print(f"  Device 2 (Laptop ini): {local_ip}:8080")
    print(f"  Device 1 (Target)    : {DEVICE1_IP}:8080")
    
    # Start HTTP server in background
    server_thread = threading.Thread(target=start_server, args=(local_ip,), daemon=True)
    server_thread.start()
    
    print("\n" + "="*50)
    print("READY! Mulai mengirim pesan...")
    print("="*50 + "\n")
    
    while True:
        try:
            plaintext = input("Masukkan plaintext: ")
            key = input("Masukkan key (8 karakter): ")
            
            print("\n--- HASIL ENKRIPSI ---")
            ciphertext = des_encrypt(plaintext, key)
            print(f"Plaintext : {plaintext}")
            print(f"Key       : {key}")
            print(f"Ciphertext: {ciphertext}")
            
            # Kirim ke Device 1
            send_to_device1(ciphertext, key)
            print("\n" + "-"*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nProgram dihentikan.")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
