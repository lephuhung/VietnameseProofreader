"""
Generate self-signed SSL certificate for VN Grammar localhost server.
Run: venv\Scripts\python.exe tools\generate_cert_py.py
"""
import os
import datetime
import subprocess
import sys

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def main():
    cert_dir = os.path.join(os.path.expanduser("~"), ".office-addin-dev-certs")
    os.makedirs(cert_dir, exist_ok=True)

    key_path = os.path.join(cert_dir, "localhost.key")
    cert_path = os.path.join(cert_dir, "localhost.crt")

    print("  [1/3] Generating RSA key + certificate...")

    # Generate RSA private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    # Build certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    now = datetime.datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365 * 5))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            ]),
            critical=False,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .sign(key, hashes.SHA256(), default_backend())
    )

    # Write private key (PEM)
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    print(f"  [OK] Key saved: {key_path}")

    # Write certificate (PEM)
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f"  [OK] Cert saved: {cert_path}")

    # Trust cert in Windows certificate store via certutil
    print("  [2/3] Trusting certificate in Windows Root store...")
    # Export as DER for certutil
    der_path = os.path.join(cert_dir, "localhost.der")
    with open(der_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.DER))

    result = subprocess.run(
        ["certutil", "-addstore", "-user", "Root", der_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  [OK] Certificate trusted in CurrentUser\\Root")
    else:
        print(f"  [WARN] certutil returned {result.returncode}: {result.stderr.strip()}")
        print("  Try running as Administrator if trust failed.")

    os.remove(der_path)

    # Verify files exist
    print("  [3/3] Verifying...")
    for p in [key_path, cert_path]:
        size = os.path.getsize(p)
        print(f"  [OK] {os.path.basename(p)}: {size} bytes")

    print()
    print("  Done! Restart the server — it should now show:")
    print("  'HTTPS Server khởi động tại https://127.0.0.1:8000'")


import ipaddress

if __name__ == "__main__":
    main()
