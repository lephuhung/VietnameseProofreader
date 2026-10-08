"""
Tạo SSL certificate tự ký cho localhost.
Tương thích với Office Add-in (HTTPS requirement).
© 2026 by thanh007
"""
import os
import sys
import subprocess
import datetime

def generate_self_signed_cert():
    """Tạo SSL cert bằng Python cryptography library."""
    cert_dir = os.path.join(os.path.expanduser("~"), ".office-addin-dev-certs")
    key_path = os.path.join(cert_dir, "localhost.key")
    cert_path = os.path.join(cert_dir, "localhost.crt")
    
    if os.path.exists(key_path) and os.path.exists(cert_path):
        print(f"[OK] SSL certificates đã tồn tại tại: {cert_dir}")
        return True

    os.makedirs(cert_dir, exist_ok=True)

    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        
        # Tạo private key
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        
        # Tạo certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VN Grammar Assistant"),
        ])
        
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )
        
        # Lưu file
        with open(key_path, "wb") as f:
            f.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))
        
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"[OK] Đã tạo SSL certificates tại: {cert_dir}")
        
        # Trust certificate trên Windows
        trust_cert_windows(cert_path)
        return True
        
    except ImportError:
        print("[WARN] Thư viện 'cryptography' chưa cài. Thử dùng openssl...")
        return generate_with_openssl(cert_dir, key_path, cert_path)


def generate_with_openssl(cert_dir, key_path, cert_path):
    """Fallback: dùng openssl nếu có."""
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", key_path, "-out", cert_path,
            "-days", "3650", "-nodes",
            "-subj", "/CN=localhost/O=VN Grammar Assistant",
            "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"
        ], check=True, capture_output=True)
        print(f"[OK] Đã tạo SSL certificates bằng openssl tại: {cert_dir}")
        trust_cert_windows(cert_path)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Không thể tạo SSL certificate.")
        print("        Cài đặt: pip install cryptography")
        return False


def trust_cert_windows(cert_path):
    """Thêm cert vào Trusted Root trên Windows."""
    try:
        subprocess.run([
            "certutil", "-addstore", "-user", "Root", cert_path
        ], check=True, capture_output=True)
        print("[OK] Đã trust certificate trên Windows.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARN] Không thể tự động trust cert. Bạn cần trust thủ công.")


import ipaddress

if __name__ == "__main__":
    generate_self_signed_cert()
