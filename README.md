# Secure File Tool

A comprehensive and interactive Streamlit-based cybersecurity application designed to demonstrate fundamental cryptographic concepts including hybrid file encryption, file hashing, and digital signatures.

## Why This Project?

Understanding cryptography conceptually is one thing, but applying it successfully is another. This project serves several purposes:
1. **Educational Tool**: An interactive dashboard showing how real-world applications use RSA and AES encryption together (Hybrid Encryption), along with hashing and signatures.
2. **Practical Utility**: While meant as a learning/demo app, it securely encrypts files, verifies integrity through standard hashing algorithms, and proves authenticity using public key infrastructure (PKI) concepts.
3. **Showcase Modern Cyber Security Libraries**: Acts as a bare-bones implementation using Python's strong open-source library `pycryptodome`.

## Cryptographic Concepts Glossary

If you are new to cybersecurity or cryptography, here is a quick breakdown of the core terms used within this project:

- **Cryptography**: The practice and study of techniques for securing communication and information against third parties, adversaries, or the public.
- **Encryption**: The process of converting plain, readable data (plaintext) into an unreadable, encoded format (ciphertext) to prevent unauthorized access.
- **Decryption**: The reverse process of encryption; transforming ciphertext back into readable plaintext using a specific key.
- **Symmetric Encryption (AES)**: A type of encryption where the *same* key is used to both encrypt and decrypt data. It is extremely fast and efficient for large files.
- **Asymmetric Encryption (RSA)**: Also known as Public-Key Cryptography. It uses a paired key system: a **Public Key** (shared with everyone) to encrypt data, and a **Private Key** (kept secretly by the owner) to decrypt data.
- **Hashing (MD5, SHA-1)**: A one-way mathematical function that transforms any amount of data into a fixed-size string of characters (a digital fingerprint). It is used to verify that a file has not been tampered with or corrupted.
- **Digital Signature**: A mathematical scheme used to verify the authenticity and integrity of a digital message or document. It conceptually operates like a handwritten signature or stamped seal, proving who created the file and that it wasn't altered in transit.
- **Non-repudiation**: The assurance that a party to a genuine communication cannot deny its authenticity. A digital signature provides non-repudiation because only the private key owner could have signed the file.

## Core Features Breakdown

### 1. Hybrid File Encryption (RSA + AES)
Instead of encrypting the entire file with RSA (which is slow and size-limited), this tool uses a "Hybrid" approach:
- **How it works?** An AES session key is randomly generated to encrypt the actual file data (fast and scalable). Then, the AES session key itself is encrypted using the recipient's RSA Public Key. Both the encrypted data and encrypted AES key are packaged together.
- **Why?** Perfect balance between the security/convenience of asymmetric cryptography (RSA) and the speed/efficiency of symmetric cryptography (AES).
- **AES Mode**: EAX mode, which offers authenticated encryption (detects if ciphertext was modified).

### 2. File Decryption
Decrypts files previously encrypted by the tool.
- **How it works?** The user's RSA Private Key decrypts the package to extract the AES session key. This AES key then unpackages and decrypts the original file data.

### 3. File Hashing (MD5 & SHA-1)
Creates a unique digital fingerprint of your file.
- **How it works?** The file is run through mathematical hashing algorithms.
- **Why?** Hash values (checksums) are used to verify file integrity. If a single byte in the file changes, the hash will change entirely. This confirms that a file has not been altered or corrupted in transit.

### 4. Create Digital Signatures
Signs a given file using an RSA Private Key.
- **How it works?** We generate a SHA-256 hash of the file and encrypt (sign) that hash with the user's RSA Private Key. This outputs a `.sig` file.
- **Why?** Digital Signatures provide non-repudiation and origin authentication. It proves exactly *who* signed the file and guarantees the file wasn't changed afterward.

### 5. Verify Digital Signatures
Validates a provided `.sig` signature against an original file.
- **How it works?** Uses the associated RSA Public Key to decrypt the signature and compare the resulting hash to a freshly computed hash of the provided file.
- **Why?** Allows anyone with the sender's public key to trust that the sender is the legitimate source of the file.

### 6. Auto-Key Generation
- **How it works?** The app dynamically creates `private_key.pem` and `public_key.pem` (2048-bit RSA) if they are missing upon startup.

## Technologies Used
- **[Python](https://www.python.org/)**: The backbone programming language.
- **[Streamlit](https://streamlit.io/)**: Provides the fast, interactive, and beautiful front-end dashboard.
- **[PyCryptodome](https://pycryptodome.readthedocs.io/)**: The cryptographic engine handling RSA, AES, Hashing, and Signatures securely.

## Installation & Setup

### Prerequisites
Make sure you have Python 3.7+ installed.

### 1. Clone or Download the Repository
Navigate to the directory where the project is saved.
```bash
cd /path/to/security_lab
```

### 2. Create a Virtual Environment (Recommended)
Keeps project dependencies isolated.
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

You can start the app directly via Streamlit:
```bash
streamlit run app.py
```

Alternatively, you can use the provided bash script to quickly handle dependencies and start the app automatically:
```bash
chmod +x run.sh
./run.sh
```

## Usage Workflow Example

1. Start the app. Your RSA keys (`public_key.pem`, `private_key.pem`) will auto-generate in the project folder.
2. Select **Encrypt File** from the sidebar, upload a local text file, and click Encrypt to download `.enc` file.
3. Select **Decrypt File**, upload the newly downloaded `.enc` file, make sure the private key path is correct, and hit decrypt.
4. Experiment with **Hashing** and generating `.sig` **Digital Signatures** to see checksums and non-repudiation in action.

## Troubleshooting

- **`No module named Crypto` / `ModuleNotFoundError: No module named 'Crypto'`**
  Streamlit is likely utilizing a globally installed python environment separate from where `requirements.txt` was loaded. Ensure your virtual environment is activated:
  ```bash
  source .venv/bin/activate
  python -m streamlit run app.py
  ```

## Important Security Warning ⚠️
While this project correctly implements high-grade encryption libraries, it is primarily meant for **demonstration and educational purposes**.
- Real-world critical implementations require robust key-management architectures (like HSMs or secure cloud vaults) rather than storing RAW `.pem` files in a local folder.
- Never share your `private_key.pem`. Keep it secured offline if possible.
in paragraph write a short note on difference between RSA and Diffi hellman algorithm
The primary difference between the RSA and Diffie-Hellman (DH) algorithms lies in their core functions and the mathematical problems they rely on. RSA is a versatile, general-purpose public-key cryptosystem based on the mathematical difficulty of factoring the product of two extremely large prime numbers; it is extensively used to directly encrypt messages and authenticate identities through digital signatures. Conversely, Diffie-Hellman is exclusively a key-exchange protocol based on the difficulty of solving discrete logarithms; it cannot be used to encrypt arbitrary messages or authenticate users. Instead, Diffie-Hellman allows two parties who have no prior knowledge of each other to securely establish a shared symmetric session key over an entirely unsecure and monitored network—without ever transmitting the key itself—whereas RSA establishes a session key by having one party generate it, recursively encrypt it with the other's public key, and send it across the network.