# FTP & FTPS Server with MCP Integration

## 📌 Project Overview

This project implements a secure FTP server using **Explicit FTPS (FTP over TLS)** and integrates it with an **MCP (Model Context Protocol) Server**.

The MCP server allows AI assistants such as Gemini and Claude to interact with the FTP server using natural language.

Users can upload, download, list, rename, delete, and manage files through MCP tools.

## 🚀 Features

### 1. FTP/FTPS Server
- Secure file transfer using Explicit FTPS.
- TLS encryption for control and data connections.
- Username and password authentication.
- File storage in a dedicated `storage/` directory.
- Configurable FTP host and port.
- Access permissions for file management.

### 2. MCP Server Integration

The MCP server connects to the FTPS server using Python's `FTP_TLS` client.

Available MCP tools:

| Tool | Description |
|---|---|
| `list_files` | Display files and folders in storage |
| `upload_file` | Upload a file to the FTP server |
| `download_file` | Download a file from the FTP server |
| `create_folder` | Create a new directory |
| `delete_file` | Delete a file or folder |
| `rename_file` | Rename a file or folder |
| `get_file_info` | Get information about a file |

### 3. Security
- FTPS authentication.
- TLS encryption.
- Environment variables for credentials.
- `.env` file for configuration.
- File path validation to prevent directory traversal.
- MCP endpoint access protection through ngrok traffic policies.

## 🛠️ Technologies Used

- Python
- PostgreSQL (not required for the FTP-only functionality)
- pyftpdlib
- FTP_TLS
- FastMCP
- MCP
- python-dotenv
- pyOpenSSL
- ngrok

## 📂 Project Structure

```text
FTP-MCP-Server/
│
├── storage/
│   └── test.txt
│
├── venv/
│
├── ftp_server.py
├── mcp_server.py
│
├── server.crt
├── server.key
│
├── .env
├── .gitignore
├── policy.yml
│
├── requirements.txt
└── README.md
```

**Note:** Do not upload your `.env`, private key, or other sensitive credentials to GitHub.

## ⚙️ Installation and Setup

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate to the project directory:

```bash
cd FTP-MCP-Server
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project directory.

Example configuration:

```env
FTP_HOST=127.0.0.1
FTP_PORT=2121
FTP_USER=your_username
FTP_PASSWORD=your_password

FTP_ROOT=storage
FTP_CERT_FILE=server.crt
FTP_KEY_FILE=server.key
```

Use your own credentials and ensure the certificate and private key files exist.

### Step 5: Start the FTP Server

```bash
python ftp_server.py
```

The FTP server runs on:

```text
127.0.0.1:2121
```

### Step 6: Start the MCP Server

Open another terminal, activate the virtual environment, and execute:

```bash
python mcp_server.py
```

The MCP HTTP server runs on:

```text
http://127.0.0.1:8000
```

Use the MCP endpoint path configured in `mcp_server.py`.

### Step 7: Expose MCP Server Using ngrok

Start ngrok:

```bash
ngrok http 8000 --traffic-policy-file policy.yml
```

ngrok generates a public HTTPS forwarding URL.

Use the complete MCP endpoint URL when configuring a supported remote MCP client.

