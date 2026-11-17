
import os
import ssl
from pathlib import Path, PurePosixPath
from ftplib import FTP_TLS
from contextlib import contextmanager

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

FTP_HOST = os.getenv("FTP_HOST", "127.0.0.1")
FTP_PORT = int(os.getenv("FTP_PORT", "2121"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")

CERT_FILE = BASE_DIR / os.getenv(
    "FTP_CERT_FILE", "server.crt"
)

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

# Create MCP server
mcp = FastMCP(
    "FTP File Manager",
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path="/s/18c9670c834b4bbcbb6ed815c1ae89c5/mcp",
    transport_security=TransportSecuritySettings(
        allowed_hosts=[
            "127.0.0.1:8000",
            "localhost:8000",
            "[::1]:8000",
            "overbuilt-slackness-reconcile.ngrok-free.dev",
            "overbuilt-slackness-reconcile.ngrok-free.dev:443"
        ]
    )
    
)


# Validate remote FTP paths
def remote_path(path: str) -> str:
    parts = PurePosixPath(path).parts

    if ".." in parts:
        raise ValueError("Parent directory access is not allowed")

    if "\x00" in path:
        raise ValueError("Invalid file path")

    return str(PurePosixPath("/" + path.lstrip("/")))


# Connect securely to FTPS
@contextmanager
def ftp_connection():

    if not FTP_USER or not FTP_PASSWORD:
        raise ValueError("FTP credentials missing in .env")

    if not CERT_FILE.exists():
        raise FileNotFoundError("FTP certificate not found")

    # Trust our generated self-signed certificate
    context = ssl.create_default_context(
        cafile=str(CERT_FILE)
    )

    ftp = FTP_TLS(context=context, timeout=30)

    try:
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASSWORD)

        # Encrypt file transfers
        ftp.prot_p()

        yield ftp

    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


# TOOL 1: List files
@mcp.tool()
def list_files(folder: str = "/") -> str:
    """Display files and folders on the FTP server."""

    folder = remote_path(folder)

    with ftp_connection() as ftp:
        items = []

        for name, facts in ftp.mlsd(folder):
            items.append({
                "name": name,
                "type": facts.get("type", "unknown"),
                "size": facts.get("size", "unknown")
            })

        return str(items)


# TOOL 2: Upload file
@mcp.tool()
def upload_file(
    local_path: str,
    remote_name: str
) -> str:
    """Upload a local computer file to the FTP server."""

    source = Path(local_path).expanduser().resolve()
    destination = remote_path(remote_name)

    if not source.is_file():
        raise FileNotFoundError("Local file not found")

    with ftp_connection() as ftp:
        with source.open("rb") as file:
            ftp.storbinary(
                f"STOR {destination}",
                file
            )

    return f"Successfully uploaded {source.name}"


# TOOL 3: Download file
@mcp.tool()
def download_file(
    remote_name: str,
    local_path: str
) -> str:
    """Download a file from FTP server to the local computer."""

    source = remote_path(remote_name)
    destination = Path(local_path).expanduser().resolve()

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with ftp_connection() as ftp:
        with destination.open("wb") as file:
            ftp.retrbinary(
                f"RETR {source}",
                file.write
            )

    return f"Successfully downloaded to {destination}"


# TOOL 4: Create folder
@mcp.tool()
def create_folder(folder_name: str) -> str:
    """Create a new folder on the FTP server."""

    folder = remote_path(folder_name)

    with ftp_connection() as ftp:
        ftp.mkd(folder)

    return f"Folder created: {folder}"


# TOOL 5: Delete file
@mcp.tool()
def delete_file(file_name: str) -> str:
    """Delete a file from the FTP server."""

    filename = remote_path(file_name)

    if filename == "/":
        raise ValueError("Cannot delete server root")

    with ftp_connection() as ftp:
        ftp.delete(filename)

    return f"File deleted: {filename}"


# TOOL 6: Rename file
@mcp.tool()
def rename_file(
    old_name: str,
    new_name: str
) -> str:
    """Rename a file on the FTP server."""

    old_path = remote_path(old_name)
    new_path = remote_path(new_name)

    with ftp_connection() as ftp:
        ftp.rename(old_path, new_path)

    return f"Renamed {old_path} to {new_path}"


# TOOL 7: Get file information
@mcp.tool()
def get_file_info(file_name: str) -> str:
    """Get the size and modification time of a file."""

    filename = remote_path(file_name)

    with ftp_connection() as ftp:
        size = ftp.size(filename)
        modified = ftp.sendcmd(
            f"MDTM {filename}"
        )

    return (
        f"File: {filename}\n"
        f"Size: {size} bytes\n"
        f"Modified: {modified}"
    )


# Start MCP server
if __name__ == "__main__":

    print("FTP MCP Server starting...")
    print(f"FTP Server: {FTP_HOST}:{FTP_PORT}")
    print(f"MCP Server: {MCP_HOST}:{MCP_PORT}")

    mcp.run(transport="streamable-http"
            )



