
import os
from dotenv import load_dotenv
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer

# Load environment variables
load_dotenv()

# Server configuration
FTP_HOST = os.getenv("FTP_HOST", "127.0.0.1")
FTP_PORT = int(os.getenv("FTP_PORT", "2121"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")

# File storage directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

os.makedirs(STORAGE_DIR, exist_ok=True)

# Certificate and private key
CERT_FILE = os.path.join(BASE_DIR, "server.crt")
KEY_FILE = os.path.join(BASE_DIR, "server.key")

if not FTP_USER or not FTP_PASSWORD:
    raise ValueError("FTP credentials missing in .env")

if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
    raise FileNotFoundError("SSL certificate or private key not found")

# Authentication
authorizer = DummyAuthorizer()

authorizer.add_user(
    FTP_USER,
    FTP_PASSWORD,
    STORAGE_DIR,
    perm="elradfmw"
)

# Configure FTPS handler
handler = TLS_FTPHandler

handler.authorizer = authorizer

# Enable TLS encryption
handler.certfile = CERT_FILE
handler.keyfile = KEY_FILE

handler.tls_control_required = True
handler.tls_data_required = True

# Create server
server = FTPServer((FTP_HOST, FTP_PORT), handler)

print("Secure FTPS Server is starting...")
print(f"Host: {FTP_HOST}")
print(f"Port: {FTP_PORT}")
print("Protocol: Explicit FTPS")
print("TLS encryption: Enabled")
print(f"Storage: {STORAGE_DIR}")

server.serve_forever()


