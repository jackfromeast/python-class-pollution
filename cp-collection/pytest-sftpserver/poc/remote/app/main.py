"""
Minimal SFTP server using pytest-sftpserver's ContentProvider.

This simulates a scenario where an application uses ContentProvider to serve
dynamic content over SFTP. The SFTP put operation maps file paths to attribute
traversal on the content object, allowing class pollution.
"""
import paramiko
import threading
import socket
from pytest_sftpserver.sftp.server import SFTPServer
from pytest_sftpserver.sftp.content_provider import ContentProvider


class AppState:
    """Application state reachable via the content object."""
    admin = False
    role = "user"


class ContentRoot:
    """Root object exposed to SFTP clients."""
    state = AppState()
    data = {"public": "hello"}


def start_sftp_server(host="0.0.0.0", port=3373):
    content_provider = ContentProvider(content_object=ContentRoot())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[*] SFTP server listening on {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        print(f"[*] Connection from {addr}")
        transport = paramiko.Transport(conn)
        host_key = paramiko.RSAKey.generate(2048)
        transport.add_server_key(host_key)
        transport.set_subsystem_handler(
            "sftp", paramiko.SFTPServer, SFTPServer, content_provider
        )
        server = paramiko.ServerInterface()
        transport.start_server(server=server)


if __name__ == "__main__":
    start_sftp_server()
