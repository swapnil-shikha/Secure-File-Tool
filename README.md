# Secure File Tool

A simple Streamlit cybersecurity demo app for:
- File encryption and decryption (RSA + AES hybrid)
- MD5 and SHA-1 hashing
- RSA digital signatures and verification

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## If You See "No module named Crypto"

This means Streamlit is running from a different Python environment than the one where packages were installed.

Use the project virtual environment:

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

On first run, the app automatically generates:
- `private_key.pem`
- `public_key.pem`
