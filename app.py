import os
from pathlib import Path

import hashlib
import streamlit as st
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

PRIVATE_KEY_PATH = "private_key.pem"
PUBLIC_KEY_PATH = "public_key.pem"
ENCRYPTED_FILE_MAGIC = b"SFT1"


def generate_keys(private_key_path: str = PRIVATE_KEY_PATH, public_key_path: str = PUBLIC_KEY_PATH) -> None:
    private_exists = Path(private_key_path).exists()
    public_exists = Path(public_key_path).exists()

    if private_exists and public_exists:
        return

    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    with open(private_key_path, "wb") as private_file:
        private_file.write(private_key)

    with open(public_key_path, "wb") as public_file:
        public_file.write(public_key)


def _load_private_key(private_key_path: str = PRIVATE_KEY_PATH) -> RSA.RsaKey:
    with open(private_key_path, "rb") as f:
        return RSA.import_key(f.read())


def _load_public_key(public_key_path: str = PUBLIC_KEY_PATH) -> RSA.RsaKey:
    with open(public_key_path, "rb") as f:
        return RSA.import_key(f.read())


def encrypt_file(file_bytes: bytes, public_key_path: str = PUBLIC_KEY_PATH) -> bytes:
    public_key = _load_public_key(public_key_path)

    session_key = get_random_bytes(32)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(file_bytes)

    # File format: MAGIC | RSA(session_key) | nonce | tag | ciphertext
    return ENCRYPTED_FILE_MAGIC + enc_session_key + cipher_aes.nonce + tag + ciphertext


def decrypt_file(encrypted_bytes: bytes, private_key_path: str = PRIVATE_KEY_PATH) -> bytes:
    private_key = _load_private_key(private_key_path)

    if not encrypted_bytes.startswith(ENCRYPTED_FILE_MAGIC):
        raise ValueError("Invalid encrypted file format.")

    rsa_key_size = private_key.size_in_bytes()
    offset = len(ENCRYPTED_FILE_MAGIC)

    enc_session_key = encrypted_bytes[offset : offset + rsa_key_size]
    offset += rsa_key_size

    nonce = encrypted_bytes[offset : offset + 16]
    offset += 16

    tag = encrypted_bytes[offset : offset + 16]
    offset += 16

    ciphertext = encrypted_bytes[offset:]

    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce=nonce)
    return cipher_aes.decrypt_and_verify(ciphertext, tag)


def generate_md5(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()


def generate_sha1(file_bytes: bytes) -> str:
    return hashlib.sha1(file_bytes).hexdigest()


def sign_file(file_bytes: bytes, private_key_path: str = PRIVATE_KEY_PATH) -> bytes:
    private_key = _load_private_key(private_key_path)
    message_hash = SHA256.new(file_bytes)
    signature = pkcs1_15.new(private_key).sign(message_hash)
    return signature


def verify_signature(
    file_bytes: bytes,
    signature_bytes: bytes,
    public_key_path: str = PUBLIC_KEY_PATH,
) -> bool:
    public_key = _load_public_key(public_key_path)
    message_hash = SHA256.new(file_bytes)

    try:
        pkcs1_15.new(public_key).verify(message_hash, signature_bytes)
        return True
    except (ValueError, TypeError):
        return False


def _ensure_keys() -> None:
    generate_keys(PRIVATE_KEY_PATH, PUBLIC_KEY_PATH)


def _render_key_status() -> None:
    col1, col2 = st.columns(2)
    with col1:
        if Path(PRIVATE_KEY_PATH).exists():
            st.success(f"Private key ready: {PRIVATE_KEY_PATH}")
        else:
            st.warning("Private key is missing.")

    with col2:
        if Path(PUBLIC_KEY_PATH).exists():
            st.success(f"Public key ready: {PUBLIC_KEY_PATH}")
        else:
            st.warning("Public key is missing.")


def main() -> None:
    st.set_page_config(page_title="Secure File Tool", page_icon=":lock:", layout="wide")

    _ensure_keys()

    st.title("Secure File Tool")
    st.caption("A compact cybersecurity dashboard for file encryption, hashing, and digital signatures.")

    with st.container(border=True):
        st.subheader("System Status")
        _render_key_status()
        st.info(
            "On first run, RSA keys are auto-generated and saved locally as "
            "private_key.pem and public_key.pem."
        )

    st.sidebar.header("Operations")
    operation = st.sidebar.radio(
        "Choose a tool",
        [
            "Encrypt File",
            "Decrypt File",
            "Generate File Hash",
            "Create Digital Signature",
            "Verify Digital Signature",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Tip: Keep keys in a secure directory for real-world usage.")

    if operation == "Encrypt File":
        with st.container(border=True):
            st.subheader("Encrypt File")
            st.write("Encrypt any uploaded file using RSA-protected AES encryption.")

            pub_key_input = st.text_input("Public key path", value=PUBLIC_KEY_PATH)
            upload = st.file_uploader("Upload file to encrypt", type=None, key="enc_upload")

            if st.button("Encrypt", use_container_width=True):
                if upload is None:
                    st.warning("Please upload a file first.")
                elif not Path(pub_key_input).exists():
                    st.warning("Public key file not found.")
                else:
                    encrypted = encrypt_file(upload.getvalue(), pub_key_input)
                    st.success("File encrypted successfully.")
                    st.download_button(
                        "Download Encrypted File",
                        data=encrypted,
                        file_name=f"{upload.name}.enc",
                        mime="application/octet-stream",
                        use_container_width=True,
                    )

    elif operation == "Decrypt File":
        with st.container(border=True):
            st.subheader("Decrypt File")
            st.write("Decrypt a previously encrypted file using your RSA private key.")

            priv_key_input = st.text_input("Private key path", value=PRIVATE_KEY_PATH)
            upload = st.file_uploader("Upload encrypted file", type=None, key="dec_upload")

            if st.button("Decrypt", use_container_width=True):
                if upload is None:
                    st.warning("Please upload an encrypted file first.")
                elif not Path(priv_key_input).exists():
                    st.warning("Private key file not found.")
                else:
                    try:
                        decrypted = decrypt_file(upload.getvalue(), priv_key_input)
                        st.success("File decrypted successfully.")
                        original_name = upload.name.replace(".enc", "")
                        st.download_button(
                            "Download Decrypted File",
                            data=decrypted,
                            file_name=original_name,
                            mime="application/octet-stream",
                            use_container_width=True,
                        )
                    except Exception:
                        st.warning("Decryption failed. Check file integrity and key pairing.")

    elif operation == "Generate File Hash":
        with st.container(border=True):
            st.subheader("Generate File Hash")
            st.write("Generate MD5 and SHA-1 fingerprints for file integrity checks.")

            upload = st.file_uploader("Upload file for hashing", type=None, key="hash_upload")

            if st.button("Generate Hashes", use_container_width=True):
                if upload is None:
                    st.warning("Please upload a file first.")
                else:
                    file_bytes = upload.getvalue()
                    md5_value = generate_md5(file_bytes)
                    sha1_value = generate_sha1(file_bytes)

                    left, right = st.columns(2)
                    with left:
                        st.success("MD5")
                        st.code(md5_value, language="text")
                    with right:
                        st.success("SHA-1")
                        st.code(sha1_value, language="text")

    elif operation == "Create Digital Signature":
        with st.container(border=True):
            st.subheader("Create Digital Signature")
            st.write("Sign a file with your RSA private key and download the signature.")

            priv_key_input = st.text_input("Private key path", value=PRIVATE_KEY_PATH)
            upload = st.file_uploader("Upload file to sign", type=None, key="sign_upload")

            if st.button("Sign File", use_container_width=True):
                if upload is None:
                    st.warning("Please upload a file first.")
                elif not Path(priv_key_input).exists():
                    st.warning("Private key file not found.")
                else:
                    signature = sign_file(upload.getvalue(), priv_key_input)
                    st.success("Digital signature created.")
                    st.download_button(
                        "Download Signature",
                        data=signature,
                        file_name=f"{upload.name}.sig",
                        mime="application/octet-stream",
                        use_container_width=True,
                    )

    elif operation == "Verify Digital Signature":
        with st.container(border=True):
            st.subheader("Verify Digital Signature")
            st.write("Validate a signature against the file and RSA public key.")

            pub_key_input = st.text_input("Public key path", value=PUBLIC_KEY_PATH)
            upload_file = st.file_uploader("Upload original file", type=None, key="verify_file")
            upload_sig = st.file_uploader("Upload signature file (.sig)", type=None, key="verify_sig")

            if st.button("Verify Signature", use_container_width=True):
                if upload_file is None or upload_sig is None:
                    st.warning("Please upload both file and signature.")
                elif not Path(pub_key_input).exists():
                    st.warning("Public key file not found.")
                else:
                    is_valid = verify_signature(
                        upload_file.getvalue(),
                        upload_sig.getvalue(),
                        pub_key_input,
                    )
                    if is_valid:
                        st.success("Signature Valid")
                    else:
                        st.warning("Signature Invalid")


if __name__ == "__main__":
    main()
