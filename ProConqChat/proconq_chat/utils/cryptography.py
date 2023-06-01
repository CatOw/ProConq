from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class AESCipher:
    def __init__(self):
        # Generate a random 32-byte key
        self.key = get_random_bytes(32)
        # Generate a random 16-byte IV
        self.iv = get_random_bytes(16)
        # Create a cipher object with the key and IV
        self.cipher = AES.new(key=self.key, mode=AES.MODE_CBC, iv=self.iv)

    def set_key(self, aes_key, aes_iv):
        # Set the new AES key
        self.key = aes_key
        # Set the new IV
        self.iv = aes_iv
        # Create a new cipher object with the updated key and IV
        self.cipher = AES.new(key=self.key, mode=AES.MODE_CBC, iv=self.iv)

    def encrypt(self, data: bytes) -> bytes:
        # Set the key and IV to ensure consistency
        self.set_key(self.key, self.iv)
        # Pad the data to be a multiple of the block size
        data = pad(data, AES.block_size)
        # Encrypt the padded data using the AES cipher
        encrypted_data = self.cipher.encrypt(data)
        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        # Set the key and IV to ensure consistency
        self.set_key(self.key, self.iv)
        # Decrypt the data using the AES cipher
        decrypted_data = self.cipher.decrypt(data)
        # Remove padding from the decrypted data
        unpadded_data = unpad(decrypted_data, AES.block_size)
        return unpadded_data


class RSACipher:
    def __init__(self):
        # Generate a new RSA key pair with a key size of 2048 bits
        self.key = RSA.generate(2048)
        # Get the public key from the RSA key pair
        self.public_key = self.key.public_key().export_key()

    def encrypt(self, data: bytes) -> bytes:
        # Import the public key and create a cipher object
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(self.public_key))
        # Encrypt the data using the RSA public key
        encrypted_data = cipher_rsa.encrypt(data)
        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        # Create a cipher object with the RSA private key
        cipher_rsa = PKCS1_OAEP.new(self.key)
        # Decrypt the data using the RSA private key
        decrypted_data = cipher_rsa.decrypt(data)
        return decrypted_data
    